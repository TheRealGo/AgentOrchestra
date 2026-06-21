from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.self_e2e_status import finalize_status_after_task_readback  # noqa: E402
from self_e2e_status_helpers import SELF_E2E_FINALIZED_TASK_FILE, write_self_exit_result  # noqa: E402


DEPTH_CANDIDATE = (
    "[Candidates]\n"
    "selfe2e-depth: disposition=integrated; "
    "summary=SelfE2E finalization depth evidence complete; "
    "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
    "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
    "main-self-exit.json closed=true auxiliary_shell_panes same-session "
    "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
)
DEPTH_CANDIDATE_BODY = DEPTH_CANDIDATE.removeprefix("[Candidates]\n")


class SelfE2EZeroIssueDeliveryStatusTests(unittest.TestCase):
    def test_deferred_queued_consultation_blocks_zero_issue_done(self) -> None:
        self.assert_status_progress_with_candidate(
            "queued-peer-response: disposition=deferred; "
            "summary=Queued consultation still needs accepted mailbox drain evidence; "
            "evidence=artifacts/tmux-send-peer-response.json\n",
            "self-e2e-unresolved:queued-consultation:queued-peer-response:deferred",
        )

    def test_deferred_input_not_ready_delivery_blocks_zero_issue_done(self) -> None:
        self.assert_status_progress_with_candidate(
            "peer-response-input-not-ready: disposition=deferred; "
            "summary=Input-not-ready peer response still lacks accepted mailbox drain evidence; "
            "evidence=artifacts/tmux-send-peer-response.json\n",
            "self-e2e-unresolved:input-not-ready:peer-response-input-not-ready:deferred",
        )

    def test_deferred_auto_drain_failed_delivery_defect_blocks_zero_issue_done(self) -> None:
        self.assert_status_progress_with_candidate(
            "auto-drain-failure: disposition=deferred; "
            "summary=Auto-drain failed before final report delivery; "
            "evidence=artifacts/tmux-send-final-report.json ledger_candidate=delivery-defect\n",
            "self-e2e-unresolved:auto-drain-failed:auto-drain-failure:deferred",
        )

    def assert_status_progress_with_candidate(self, candidate: str, blocker: str) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                SELF_E2E_FINALIZED_TASK_FILE.replace(DEPTH_CANDIDATE, f"[Candidates]\n{candidate}{DEPTH_CANDIDATE_BODY}"),
                encoding="utf-8",
            )
            write_self_exit_result(status_file)

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertIn(blocker, result.blockers)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")


if __name__ == "__main__":
    unittest.main()
