from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.cli import main as cli_main  # noqa: E402
from agent_orchestra_minimal.codex_features import CodexFeatureReport  # noqa: E402
from agent_orchestra_minimal.codex_features import parse_codex_features_list, summarize_codex_features  # noqa: E402
from agent_orchestra_minimal.doctor import doctor_command, inspect_task_file, run_codex_doctor, summarize_codex_doctor  # noqa: E402
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class CodexConfigContractTests(unittest.TestCase):
    def test_launch_config_escapes_toml_path_keys(self) -> None:
        with tempfile.TemporaryDirectory(prefix='agent"orchestra-') as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
            )

            config = material.config_path.read_text(encoding="utf-8")

        escaped_workspace = _toml_key_text(str(material.workspace))
        self.assertIn(f'[projects."{escaped_workspace}"]', config)
        self.assertIn('trust_level = "trusted"', config)
        state_key = f"{material.config_path}:stop:0:0"
        escaped_state_key = _toml_key_text(state_key)
        self.assertIn(f'[hooks.state."{escaped_state_key}"]', config)
        self.assertIn(r"agent\"orchestra-", config)

    def test_codex_doctor_summarizes_ok_report_as_non_failing(self) -> None:
        report = summarize_codex_doctor(
            {
                "overallStatus": "ok",
                "codexVersion": "0.135.0",
                "checks": {
                    "auth.credentials": {
                        "category": "auth",
                        "status": "ok",
                        "summary": "auth is configured",
                    }
                },
            },
            returncode=0,
        )

        self.assertFalse(report.failed)
        self.assertEqual(report.lines, ["Codex doctor ok version=0.135.0"])

    def test_codex_doctor_summarizes_warning_without_failing_when_exit_code_is_zero(self) -> None:
        report = summarize_codex_doctor(
            {
                "overallStatus": "warning",
                "codexVersion": "0.135.0",
                "checks": {
                    "network.websocket_reachability": {
                        "category": "websocket",
                        "status": "warning",
                        "summary": "Responses WebSocket failed; HTTPS fallback may still work",
                        "remediation": "Check proxy policy.",
                    }
                },
            },
            returncode=0,
        )

        self.assertFalse(report.failed)
        self.assertIn("overallStatus=warning version=0.135.0", report.lines[0])
        self.assertIn("websocket/network.websocket_reachability", report.lines[1])
        self.assertIn("Check proxy policy.", report.lines[1])

    def test_codex_doctor_summarizes_fail_report_as_failing(self) -> None:
        report = summarize_codex_doctor(
            {
                "overallStatus": "fail",
                "codexVersion": "0.135.0",
                "checks": {
                    "network.provider_reachability": {
                        "category": "reachability",
                        "status": "fail",
                        "summary": "one or more required provider endpoints are unreachable over HTTP",
                    }
                },
            },
            returncode=1,
        )

        self.assertTrue(report.failed)
        self.assertIn("reachability/network.provider_reachability", report.lines[1])

    def test_codex_doctor_reports_invalid_json(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=args, returncode=1, stdout="not json", stderr="")

        report = run_codex_doctor(timeout_seconds=3, runner=runner)

        self.assertTrue(report.failed)
        self.assertIn("invalid JSON", report.lines[0])

    def test_codex_doctor_reports_non_object_json(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=args, returncode=1, stdout="[]", stderr="")

        report = run_codex_doctor(timeout_seconds=3, runner=runner)

        self.assertTrue(report.failed)
        self.assertEqual(report.lines, ["Codex doctor returned JSON list, expected object"])

    def test_codex_doctor_reports_timeout(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            raise subprocess.TimeoutExpired(cmd=["codex", "doctor", "--json"], timeout=3)

        report = run_codex_doctor(timeout_seconds=3, runner=runner)

        self.assertTrue(report.failed)
        self.assertEqual(report.lines, ["Codex doctor timed out after 3s"])

    def test_codex_features_parser_summarizes_0137_feature_list(self) -> None:
        output = """
Feature              Status
hooks                enabled
multi_agent          disabled
unified_exec         enabled
shell_snapshot       disabled
prevent_idle_sleep   disabled
"""
        features = parse_codex_features_list(output)
        report = summarize_codex_features(output)

        self.assertEqual(features["hooks"], "enabled")
        self.assertEqual(features["multi_agent"], "disabled")
        self.assertEqual(features["unified_exec"], "enabled")
        self.assertEqual(features["shell_snapshot"], "disabled")
        self.assertEqual(features["prevent_idle_sleep"], "disabled")
        self.assertEqual(
            report.lines,
            [
                "Codex features hooks=enabled, multi_agent=disabled, "
                "unified_exec=enabled, shell_snapshot=disabled, prevent_idle_sleep=disabled"
            ],
        )

    def test_codex_features_parser_prefers_disabled_over_enable_hint(self) -> None:
        output = "prevent_idle_sleep disabled; use --enable prevent_idle_sleep to opt in"

        features = parse_codex_features_list(output)

        self.assertEqual(features["prevent_idle_sleep"], "disabled")

    def test_codex_features_parser_treats_explicit_unsupported_feature_as_absent(self) -> None:
        outputs = (
            "prevent_idle_sleep is not supported by this Codex build",
            "prevent_idle_sleep unavailable",
            "unknown feature prevent_idle_sleep",
        )

        for output in outputs:
            with self.subTest(output=output):
                features = parse_codex_features_list(output)

                self.assertEqual(features["prevent_idle_sleep"], "absent")

    def test_codex_doctor_cli_default_timeout_is_60_seconds(self) -> None:
        with patch("agent_orchestra_minimal.cli.doctor_command", return_value=0) as doctor:
            result = cli_main(["doctor", "--target-project", str(ROOT), "--codex-doctor"])

        self.assertEqual(result, 0)
        args = doctor.call_args.args[0]
        self.assertEqual(args.codex_doctor_timeout_seconds, 60.0)

    def test_codex_doctor_cli_accepts_codex_features_flag(self) -> None:
        with patch("agent_orchestra_minimal.cli.doctor_command", return_value=0) as doctor:
            result = cli_main(["doctor", "--target-project", str(ROOT), "--codex-features"])

        self.assertEqual(result, 0)
        args = doctor.call_args.args[0]
        self.assertTrue(args.codex_features)

    def test_doctor_cli_accepts_task_file_flag(self) -> None:
        with patch("agent_orchestra_minimal.cli.doctor_command", return_value=0) as doctor:
            result = cli_main(["doctor", "--target-project", str(ROOT), "--task-file", "/tmp/tasks.ini"])

        self.assertEqual(result, 0)
        args = doctor.call_args.args[0]
        self.assertEqual(args.task_file, "/tmp/tasks.ini")

    def test_codex_features_doctor_reports_success(self) -> None:
        report = CodexFeatureReport(
            failed=False,
            features={"prevent_idle_sleep": "disabled"},
            lines=["Codex features prevent_idle_sleep=disabled"],
        )
        args = _doctor_args(codex_features=True)

        with patch("agent_orchestra_minimal.doctor.codex_auth_available", return_value=True), \
             patch("agent_orchestra_minimal.doctor.command_available", return_value=True), \
             patch("agent_orchestra_minimal.doctor.run_codex_features_list", return_value=report), \
             patch.dict("os.environ", {"TMUX": "tmux-session"}, clear=False):
            result = doctor_command(args)

        self.assertEqual(result, 0)

    def test_codex_features_doctor_fails_when_feature_probe_fails(self) -> None:
        report = CodexFeatureReport(
            failed=True,
            features={},
            lines=["Codex features list could not run: missing codex"],
        )
        args = _doctor_args(codex_features=True)

        with patch("agent_orchestra_minimal.doctor.codex_auth_available", return_value=True), \
             patch("agent_orchestra_minimal.doctor.command_available", return_value=True), \
             patch("agent_orchestra_minimal.doctor.run_codex_features_list", return_value=report), \
             patch.dict("os.environ", {"TMUX": "tmux-session"}, clear=False):
            result = doctor_command(args)

        self.assertEqual(result, 1)

    def test_task_file_doctor_reports_finalized_task_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")

            report = inspect_task_file(task_file)

        self.assertFalse(report.failed)
        self.assertIn("shared task file finalized", report.lines[0])

    def test_task_file_doctor_reports_finalization_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(
                DEFAULT_TASK_FILE.replace("[status]\ndone", "[status]\nprogress").replace(
                    "[InReview]\n\n",
                    "[InReview]\nreview pending\n\n",
                ),
                encoding="utf-8",
            )

            report = inspect_task_file(task_file)

        self.assertTrue(report.failed)
        self.assertIn("shared task file has finalization blockers:", report.lines)
        self.assertIn("  status=progress", report.lines)
        self.assertIn("  open:review pending", report.lines)


def _toml_key_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _doctor_args(**overrides: object) -> object:
    class Args:
        target_project = str(ROOT)
        tui_transport = False
        codex_doctor = False
        codex_doctor_timeout_seconds = 60.0
        codex_features = False
        task_file = None

    args = Args()
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


if __name__ == "__main__":
    unittest.main()
