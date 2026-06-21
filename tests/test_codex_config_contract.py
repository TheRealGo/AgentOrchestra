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
from agent_orchestra_minimal.doctor import McpDoctorReport, doctor_command, inspect_task_file, run_codex_doctor, summarize_codex_doctor  # noqa: E402
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
                    "mcp.colab-mcp.handshake": {
                        "category": "mcp",
                        "status": "fail",
                        "summary": "colab-mcp handshake failed with token=secret-value",
                        "remediation": "Check COLAB_TOKEN=secret-value and rerun doctor --mcp.",
                    }
                },
            },
            returncode=1,
        )

        output = "\n".join(report.lines)
        self.assertTrue(report.failed)
        self.assertIn("mcp/mcp.colab-mcp.handshake", output)
        self.assertIn("handshake failed", output)
        self.assertIn("token=<redacted>", output)
        self.assertIn("COLAB_TOKEN=<redacted>", output)
        self.assertNotIn("secret-value", output)

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

    def test_mcp_doctor_does_not_require_tmux_transport(self) -> None:
        args = _doctor_args(mcp=True)

        with patch("agent_orchestra_minimal.doctor.codex_auth_available", return_value=True), \
             patch("agent_orchestra_minimal.doctor.command_available", return_value=True), \
             patch("agent_orchestra_minimal.doctor.inspect_mcp", return_value=McpDoctorReport(failed=False, lines=[])), \
             patch.dict("os.environ", {}, clear=True):
            result = doctor_command(args)

        self.assertEqual(result, 0)

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

    def test_task_file_doctor_reports_duplicate_gate_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(
                DEFAULT_TASK_FILE.replace(
                    "[Gates]\n\n",
                    (
                        "[Gates]\n"
                        "gate-e2e-api: status=open; kind=e2e; evidence=pending\n"
                        "gate-e2e-api: status=passed; kind=e2e; evidence=api-smoke\n\n"
                    ),
                ),
                encoding="utf-8",
            )

            report = inspect_task_file(task_file)

        self.assertTrue(report.failed)
        self.assertIn("shared task file has finalization blockers:", report.lines)
        self.assertIn(
            "  gate-duplicate:gate-e2e-api: status=passed; kind=e2e; evidence=api-smoke",
            report.lines,
        )
        self.assertIn(
            "  gate:gate-e2e-api: status=open; kind=e2e; evidence=pending",
            report.lines,
        )

    def test_task_file_doctor_reports_unretired_professional_agent_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_file = root / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            agent_dir = root / "agents" / "pa-implementation-08"
            agent_dir.mkdir(parents=True)
            state = '{"agent_id":"pa-implementation-08","agent_kind":"ProfessionalAgent","state":"ready","tmux_target":"%169"}\n'
            (agent_dir / "state.json").write_text(state, encoding="utf-8")

            report = inspect_task_file(task_file)

        self.assertTrue(report.failed)
        self.assertIn("shared task file has finalization blockers:", report.lines)
        self.assertIn(
            "  agent-state:pa-implementation-08: ProfessionalAgent not retired: ready",
            report.lines,
        )


def _toml_key_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _doctor_args(**overrides: object) -> object:
    class Args:
        target_project = str(ROOT)
        tui_transport = False
        codex_doctor = False
        codex_doctor_timeout_seconds = 60.0
        codex_features = False
        mcp = False
        task_file = None

    args = Args()
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


if __name__ == "__main__":
    unittest.main()
