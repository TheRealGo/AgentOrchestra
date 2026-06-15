from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.cli import default_run_root, main as cli_main  # noqa: E402
from agent_orchestra_minimal.doctor import inspect_server_processes  # noqa: E402


class DoctorServerProcessTests(unittest.TestCase):
    def test_doctor_cli_accepts_server_processes_flag(self) -> None:
        with patch("agent_orchestra_minimal.cli.doctor_command", return_value=0) as doctor:
            result = cli_main(["doctor", "--target-project", str(ROOT), "--server-processes"])

        self.assertEqual(result, 0)
        args = doctor.call_args.args[0]
        self.assertTrue(args.server_processes)
        self.assertEqual(args.server_process_root, str(default_run_root()))

    def test_server_process_doctor_reports_live_recorded_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "run" / "agents" / "main" / "env" / "server-processes.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps(
                    {
                        "web": {
                            "status": "running",
                            "pid": 1234,
                            "base_url": "http://127.0.0.1:3000",
                        },
                        "old": {"status": "stopped", "pid": 5678},
                    }
                ),
                encoding="utf-8",
            )

            report = inspect_server_processes(root, alive_checker=lambda pid: pid == 1234)

        self.assertTrue(report.failed)
        output = "\n".join(report.lines)
        self.assertIn("live server processes remain", output)
        self.assertIn("web status=running pid=1234", output)
        self.assertNotIn("old status=stopped", output)

    def test_server_process_doctor_passes_when_no_live_helpers_remain(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            manifest.write_text(json.dumps({"web": {"status": "running", "pid": 1234}}), encoding="utf-8")

            report = inspect_server_processes(root, alive_checker=lambda pid: False)

        self.assertFalse(report.failed)
        self.assertIn("no live server processes recorded", report.lines)


if __name__ == "__main__":
    unittest.main()
