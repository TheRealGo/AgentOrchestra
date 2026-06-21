from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.cli import main as cli_main  # noqa: E402
from agent_orchestra_minimal.self_e2e_status import finalize_status_after_task_readback  # noqa: E402
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE, SharedTaskFile  # noqa: E402


class ServiceE2EIntakeCliTests(unittest.TestCase):
    def test_cli_appends_service_e2e_brief_to_task_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_file = Path(tmp) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = cli_main(
                    [
                        "service-e2e-intake",
                        "--brief",
                        "ServiceE2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases.",
                        "--task-file",
                        str(task_file),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertIn("[Acceptance]", stdout.getvalue())
            self.assertIn("appended to", stderr.getvalue())
            parsed = SharedTaskFile.read(task_file)
            self.assertEqual(parsed.status, "progress")
            self.assertIn(
                "service-e2e-approval-replay-browser-evidence-rerun",
                "\n".join(parsed.sections["Backlog"]),
            )

    def test_cli_brief_file_routes_worker_observations_into_task_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            brief_file = root / "service-e2e-agent-orchestra-defects.md"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            brief_file.write_text(
                "ServiceE2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases.",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = cli_main(
                    [
                        "service-e2e-intake",
                        "--brief-file",
                        str(brief_file),
                        "--task-file",
                        str(task_file),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertIn("appended to", stderr.getvalue())
            parsed = SharedTaskFile.read(task_file)
            self.assertEqual(parsed.status, "progress")
            for section in ("Backlog", "Acceptance", "Gates", "Candidates"):
                joined = "\n".join(parsed.sections[section])
                self.assertIn("service-e2e-approval-replay-browser-evidence-rerun", joined)
                self.assertIn("service-e2e-approval-replay-run-scoped-docker-volume-cleanup", joined)
            self.assertIn("UserNeeded disposition autonomy_blocker", stdout.getvalue())

    def test_cli_intake_output_keeps_selfe2e_status_progress_until_ledger_is_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = cli_main(
                    [
                        "service-e2e-intake",
                        "--brief",
                        "ServiceE2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases.",
                        "--task-file",
                        str(task_file),
                    ]
                )

            self.assertEqual(rc, 0)
            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertFalse(result.task_finalized)
            self.assertIn("status=progress", result.blockers)
            self.assertTrue(
                any(
                    "open:service-e2e-approval-replay-browser-evidence-rerun" in blocker
                    for blocker in result.blockers
                )
            )
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")


if __name__ == "__main__":
    unittest.main()
