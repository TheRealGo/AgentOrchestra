from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.self_e2e_status import (  # noqa: E402
    TaskFileNotFinalizedError,
    write_done_after_task_finalization,
)
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from self_e2e_status_helpers import SELF_E2E_FINALIZED_TASK_FILE, write_self_exit_result  # noqa: E402


class SelfE2EStatusTests(unittest.TestCase):
    def test_done_status_requires_finalized_task_file_readback_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(status_file)

            result = write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertEqual(result.value, "done")
            self.assertEqual(result.readback, "done")
            self.assertEqual(status_file.read_text(encoding="utf-8"), "done")

    def test_structurally_finalized_empty_task_file_is_not_enough_for_selfe2e_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")

            with self.assertRaises(TaskFileNotFinalizedError) as raised:
                write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertIn("self-e2e-missing:service-approval-replay", raised.exception.blockers)
            self.assertIn("self-e2e-missing:execution-path-proof", raised.exception.blockers)
            self.assertIn("self-e2e-missing:multi-viewpoint-search", raised.exception.blockers)
            self.assertIn("self-e2e-missing:professional-agent-review", raised.exception.blockers)
            self.assertIn("self-e2e-missing:standard-verification", raised.exception.blockers)
            self.assertIn("self-e2e-missing:final-candidate-sweep", raised.exception.blockers)
            self.assertIn("self-e2e-missing:cao-intervention-disposition", raised.exception.blockers)
            self.assertIn("self-e2e-missing:live-main-self-exit-json", raised.exception.blockers)
            self.assertIn("self-e2e-missing:same-session-auxiliary-shell-cleanup", raised.exception.blockers)
            self.assertIn("self-e2e-missing:no-cao-cleanup", raised.exception.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_service_approval_replay_requires_worker_intake_path_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                SELF_E2E_FINALIZED_TASK_FILE.replace("service-e2e-intake worker-path ", ""),
                encoding="utf-8",
            )
            write_self_exit_result(status_file)

            with self.assertRaises(TaskFileNotFinalizedError) as raised:
                write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertIn("self-e2e-missing:service-approval-replay", raised.exception.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_service_approval_replay_requires_all_worker_observation_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                SELF_E2E_FINALIZED_TASK_FILE.replace(
                    "service-e2e-approval-replay-run-scoped-docker-volume-cleanup",
                    "",
                ),
                encoding="utf-8",
            )
            write_self_exit_result(status_file)

            with self.assertRaises(TaskFileNotFinalizedError) as raised:
                write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertIn(
                "self-e2e-missing:service-approval-replay:run-scoped-docker-volume-cleanup",
                raised.exception.blockers,
            )
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_selfe2e_depth_requires_search_and_standard_verification_evidence(self) -> None:
        for token, blocker in (
            ("multi-viewpoint-search ", "self-e2e-missing:multi-viewpoint-search"),
            ("standard-verification ", "self-e2e-missing:standard-verification"),
        ):
            with self.subTest(token=token), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                task_file = root / "tasks.ini"
                status_file = root / ".tmp" / "self-improvement-e2e" / "status"
                task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE.replace(token, ""), encoding="utf-8")
                write_self_exit_result(status_file)

                with self.assertRaises(TaskFileNotFinalizedError) as raised:
                    write_done_after_task_finalization(task_file=task_file, status_file=status_file)

                self.assertIn(blocker, raised.exception.blockers)
                self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_textual_self_exit_evidence_without_json_keeps_status_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")

            with self.assertRaises(TaskFileNotFinalizedError) as raised:
                write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertIn("self-e2e-missing:live-main-self-exit-json", raised.exception.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_wrong_session_self_exit_json_keeps_status_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(status_file, session_name="CAO")

            with self.assertRaises(TaskFileNotFinalizedError) as raised:
                write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertIn(
                "self-e2e-invalid:same-session-auxiliary-shell-cleanup:session-prefix",
                raised.exception.blockers,
            )
            self.assertIn("self-e2e-invalid:no-cao-cleanup", raised.exception.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_prior_cao_cleanup_evidence_is_not_enough_for_selfe2e_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                SELF_E2E_FINALIZED_TASK_FILE.replace(
                    "copied-runtime main-self-exit.json closed=true auxiliary_shell_panes same-session dedicated-session-gone active-main-session pane session no-CAO-cleanup",
                    "CAO-cleanup parent-helper main-self-exit JSON",
                ),
                encoding="utf-8",
            )

            with self.assertRaises(TaskFileNotFinalizedError) as raised:
                write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertIn("self-e2e-missing:live-main-self-exit-json", raised.exception.blockers)
            self.assertIn("self-e2e-missing:same-session-auxiliary-shell-cleanup", raised.exception.blockers)
            self.assertIn("self-e2e-missing:dedicated-session-gone", raised.exception.blockers)
            self.assertIn("self-e2e-missing:no-cao-cleanup", raised.exception.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_done_status_is_not_written_while_task_file_has_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks.ini"
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            status_file.parent.mkdir(parents=True)
            status_file.write_text("progress", encoding="utf-8")
            task_file.write_text(
                DEFAULT_TASK_FILE.replace(
                    "[status]\ndone",
                    "[status]\nprogress",
                ).replace(
                    "[InProgress]\n\n",
                    "[InProgress]\nCU-001: owner_dri=main; evidence=pending\n\n",
                ),
                encoding="utf-8",
            )

            with self.assertRaises(TaskFileNotFinalizedError) as raised:
                write_done_after_task_finalization(task_file=task_file, status_file=status_file)

            self.assertIn("status=progress", raised.exception.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

if __name__ == "__main__":
    unittest.main()
