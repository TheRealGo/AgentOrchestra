from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.self_e2e_status import (  # noqa: E402
    finalize_status_after_task_readback,
)
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from self_e2e_status_helpers import SELF_E2E_FINALIZED_TASK_FILE, write_self_exit_result  # noqa: E402


class SelfE2EStatusFinalizationTests(unittest.TestCase):
    def test_unresolved_task_file_keeps_status_progress_and_reports_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                DEFAULT_TASK_FILE.replace("[status]\ndone", "[status]\nprogress").replace(
                    "[InProgress]\n\n",
                    "[InProgress]\nCU-001: owner_dri=main; evidence=pending\n\n",
                ),
                encoding="utf-8",
            )
            status_file.parent.mkdir(parents=True)
            status_file.write_text("done", encoding="utf-8")

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertEqual(result.observed, "progress")
            self.assertFalse(result.task_finalized)
            self.assertIn("status=progress", result.blockers)
            self.assertIn("open:CU-001: owner_dri=main; evidence=pending", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_unresolved_copy_local_approval_candidate_keeps_status_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                DEFAULT_TASK_FILE.replace("[status]\ndone", "[status]\nprogress").replace(
                    "[Candidates]\n\n",
                    (
                        "[Candidates]\n"
                        "copy-local-approval-intervention: disposition=open; "
                        "summary=CAO approved in-scope generated-copy edit; "
                        "evidence=.tmp/self-improvement-e2e/observed-defects-20260621-round3.md\n\n"
                    ),
                ),
                encoding="utf-8",
            )
            status_file.parent.mkdir(parents=True)
            status_file.write_text("done", encoding="utf-8")

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertEqual(result.observed, "progress")
            self.assertFalse(result.task_finalized)
            self.assertIn("status=progress", result.blockers)
            self.assertIn(
                "candidate:copy-local-approval-intervention: disposition=open; "
                "summary=CAO approved in-scope generated-copy edit; "
                "evidence=.tmp/self-improvement-e2e/observed-defects-20260621-round3.md",
                result.blockers,
            )
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_unresolved_cao_intervention_candidate_keeps_status_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                DEFAULT_TASK_FILE.replace(
                    "[Candidates]\n\n",
                    (
                        "[Candidates]\n"
                        "cao-approval: disposition=open; "
                        "summary=CAO approved copy-local edit during SelfE2E; "
                        "evidence=artifacts/approval-prompt.json\n\n"
                    ),
                ),
                encoding="utf-8",
            )
            status_file.parent.mkdir(parents=True)
            status_file.write_text("done", encoding="utf-8")

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertEqual(result.observed, "progress")
            self.assertIn(
                "candidate:cao-approval: disposition=open; "
                "summary=CAO approved copy-local edit during SelfE2E; "
                "evidence=artifacts/approval-prompt.json",
                result.blockers,
            )
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_round6_delivery_retirement_and_session_boundary_candidates_keep_status_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            candidate_lines = (
                "round6-pa-final-delivery: disposition=open; "
                "summary=PA final report delivery degraded; "
                "evidence=.tmp/self-improvement-e2e/observed-defects-20260621-round6.md\n"
                "round6-pa-exit-residue: disposition=open; "
                "summary=PA /exit composer residue; "
                "evidence=.tmp/self-improvement-e2e/observed-defects-20260621-round6.md\n"
                "round6-session-boundary: disposition=open; "
                "summary=session boundary ambiguity; "
                "evidence=.tmp/self-improvement-e2e/observed-defects-20260621-round6.md\n"
            )
            task_file.write_text(
                DEFAULT_TASK_FILE.replace("[Candidates]\n\n", f"[Candidates]\n{candidate_lines}\n"),
                encoding="utf-8",
            )
            status_file.parent.mkdir(parents=True)
            status_file.write_text("done", encoding="utf-8")

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertEqual(result.observed, "progress")
            self.assertFalse(result.task_finalized)
            for candidate in (
                "round6-pa-final-delivery",
                "round6-pa-exit-residue",
                "round6-session-boundary",
            ):
                self.assertTrue(any(f"candidate:{candidate}:" in blocker for blocker in result.blockers))
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_structurally_finalized_empty_task_file_keeps_status_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertEqual(result.observed, "progress")
            self.assertFalse(result.task_finalized)
            self.assertIn("self-e2e-missing:service-approval-replay", result.blockers)
            self.assertIn("self-e2e-missing:execution-path-proof", result.blockers)
            self.assertIn("self-e2e-missing:multi-viewpoint-search", result.blockers)
            self.assertIn("self-e2e-missing:professional-agent-review", result.blockers)
            self.assertIn("self-e2e-missing:standard-verification", result.blockers)
            self.assertIn("self-e2e-missing:final-candidate-sweep", result.blockers)
            self.assertIn("self-e2e-missing:cao-intervention-disposition", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_finalized_task_file_with_selfe2e_depth_evidence_writes_done_and_reads_back_same_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(status_file)

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "done")
            self.assertEqual(result.observed, "done")
            self.assertTrue(result.task_finalized)
            self.assertEqual(result.blockers, ())
            self.assertEqual(status_file.read_text(encoding="utf-8"), "done")

    def test_self_exit_evidence_must_name_json_artifact_before_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                SELF_E2E_FINALIZED_TASK_FILE.replace("main-self-exit.json", "main-self-exit"),
                encoding="utf-8",
            )
            write_self_exit_result(status_file)

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-missing:live-main-self-exit-json", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_self_exit_evidence_must_read_actual_json_before_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-missing:live-main-self-exit-json", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_self_exit_json_must_prove_closed_same_session_and_no_cao_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(
                status_file,
                closed=False,
                session_name="CAO",
                auxiliary_shell_panes=[],
                reason="CAO cleanup",
            )

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-invalid:live-main-self-exit-json:closed-not-true", result.blockers)
            self.assertIn(
                "self-e2e-invalid:same-session-auxiliary-shell-cleanup:session-prefix",
                result.blockers,
            )
            self.assertIn("self-e2e-invalid:no-cao-cleanup", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_self_exit_json_must_prove_dedicated_session_is_gone(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            write_self_exit_result(status_file, session_gone=False)

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn("self-e2e-invalid:dedicated-session-gone", result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_tracked_tests_do_not_read_ignored_self_e2e_tmp_fixtures(self) -> None:
        offenders: list[str] = []

        for path in sorted((ROOT / "tests").glob("test_*.py")):
            if path == Path(__file__).resolve():
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if ".tmp/self-improvement-e2e/" in line and (
                    "read_text(" in line or "open(" in line
                ):
                    offenders.append(f"{path.relative_to(ROOT)}:{line_number}")

        self.assertEqual(offenders, [])

if __name__ == "__main__":
    unittest.main()
