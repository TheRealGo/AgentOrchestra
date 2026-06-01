from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.doctor import run_codex_doctor, summarize_codex_doctor  # noqa: E402
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


def _toml_key_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    unittest.main()
