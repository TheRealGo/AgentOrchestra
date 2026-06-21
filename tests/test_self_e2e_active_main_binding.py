from __future__ import annotations

import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.self_e2e_status import finalize_status_after_task_readback  # noqa: E402
from self_e2e_status_helpers import SELF_E2E_FINALIZED_TASK_FILE, write_self_exit_result  # noqa: E402


class SelfE2EActiveMainBindingTests(unittest.TestCase):
    def test_self_exit_json_must_be_bound_to_recorded_active_main_pane_and_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file, status_file = self._paths(Path(tmpdir))
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(
                status_file,
                pane="%447",
                session_name="AgentOrchestra-self-e2e-final-20260621-201803-58928",
                active_pane="%439",
                active_session_name="AgentOrchestra-self-e2e-20260621-200315",
            )

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-invalid:active-main-session-binding:pane-mismatch", result.blockers)
            self.assertIn("self-e2e-invalid:active-main-session-binding:session-mismatch", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_newer_proof_session_json_blocks_even_when_older_active_main_json_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file, status_file = self._paths(Path(tmpdir))
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(
                status_file,
                pane="%439",
                session_name="AgentOrchestra-self-e2e-20260621-200315",
                active_pane="%439",
                active_session_name="AgentOrchestra-self-e2e-20260621-200315",
            )
            self._write_proof_session_json(status_file)

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-invalid:active-main-session-binding:pane-mismatch", result.blockers)
            self.assertIn("self-e2e-invalid:active-main-session-binding:session-mismatch", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_self_exit_json_without_active_main_binding_keeps_status_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file, status_file = self._paths(Path(tmpdir))
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(status_file, write_active_main=False)

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-missing:active-main-session-binding", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_latest_self_exit_json_must_match_active_main_even_if_older_json_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file, status_file = self._paths(Path(tmpdir))
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(
                status_file,
                pane="%439",
                session_name="AgentOrchestra-self-e2e-20260621-200315",
                active_pane="%439",
                active_session_name="AgentOrchestra-self-e2e-20260621-200315",
            )
            older = status_file.parent / "main-self-exit.json"
            time.sleep(0.01)
            (status_file.parent / "main-self-exit-proof.json").write_text(
                older.read_text(encoding="utf-8")
                .replace("%439", "%447")
                .replace(
                    "AgentOrchestra-self-e2e-20260621-200315",
                    "AgentOrchestra-self-e2e-final-20260621-201803-58928",
                ),
                encoding="utf-8",
            )

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-invalid:active-main-session-binding:pane-mismatch", result.blockers)
            self.assertIn("self-e2e-invalid:active-main-session-binding:session-mismatch", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def _paths(self, tmp: Path) -> tuple[Path, Path]:
        return tmp / "tasks.ini", tmp / ".tmp" / "self-improvement-e2e" / "status"

    def _write_proof_session_json(self, status_file: Path) -> None:
        (status_file.parent / "main-self-exit-proof-20260621-201746.json").write_text(
            (
                '{"attempts": 0, "auxiliary_shell_panes": ["%446"], '
                '"cleared_leftover": false, "closed": true, "killed_pane": true, '
                '"pane": "%444", "reason": "dedicated_session_shell_cleanup", '
                '"session_name": "AgentOrchestra-self-e2e-proof-20260621-201746-57446"}\n'
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
