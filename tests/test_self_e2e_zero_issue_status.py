from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.self_e2e_status import finalize_status_after_task_readback  # noqa: E402
from agent_orchestra_minimal.autonomy_policy import SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS  # noqa: E402
from self_e2e_status_helpers import SELF_E2E_FINALIZED_TASK_FILE, write_self_exit_result  # noqa: E402


class SelfE2EZeroIssueStatusTests(unittest.TestCase):
    def test_deferred_zero_issue_blocker_keeps_status_progress_despite_complete_depth_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(
                SELF_E2E_FINALIZED_TASK_FILE.replace(
                    "selfe2e-depth: disposition=integrated; "
                    "summary=SelfE2E finalization depth evidence complete; ",
                    "selfe2e-depth: disposition=deferred; "
                    "summary=degraded delivery still needs later clean SelfE2E proof; ",
                ),
                encoding="utf-8",
            )
            write_self_exit_result(status_file)

            result = finalize_status_after_task_readback(
                status_path=status_file,
                task_file_path=task_file,
            )

            self.assertEqual(result.status, "progress")
            self.assertFalse(result.task_finalized)
            self.assertIn(
                "self-e2e-unresolved:degraded-delivery:selfe2e-depth:deferred",
                result.blockers,
            )
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_resolved_cao_intervention_candidate_still_blocks_zero_issue_done(self) -> None:
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            "[Candidates]\n"
            "selfe2e-depth: disposition=integrated; "
            "summary=SelfE2E finalization depth evidence complete; "
            "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
                "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
            "main-self-exit.json closed=true auxiliary_shell_panes same-session "
            "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n",
            (
                "[Candidates]\n"
                "cao-copy-edit: disposition=deferred; "
                "summary=CAO intervention remains for generated-copy edit; "
                "evidence=.tmp/self-improvement-e2e/observed-defects.md\n"
                "selfe2e-depth: disposition=integrated; "
                "summary=SelfE2E finalization depth evidence complete; "
                "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
                "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
                "main-self-exit.json closed=true auxiliary_shell_panes same-session "
                "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
            ),
        )
        self.assert_status_progress_with_blocker(
            task_text,
            "self-e2e-unresolved:cao-intervention:cao-copy-edit:deferred",
        )

    def test_resolved_degraded_delivery_acceptance_still_blocks_zero_issue_done(self) -> None:
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            "[Acceptance]\n"
            "REQ-001: status=satisfied; source=SPEC.md; owner=main; "
            "verification=selfe2e-finalization; "
            "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
                "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
            "main-self-exit.json closed=true auxiliary_shell_panes same-session "
            "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n",
            (
                "[Acceptance]\n"
                "REQ-001: status=satisfied; source=SPEC.md; owner=main; "
                "verification=selfe2e-finalization; "
                "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
                "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
                "main-self-exit.json closed=true auxiliary_shell_panes same-session "
                "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n"
                "REQ-PA-DELIVERY: status=deferred; source=selfe2e-observation; "
                "owner=main; verification=degraded delivery remains pending later clean live E2E; "
                "evidence=.tmp/self-improvement-e2e/observed-defects.md\n\n"
            ),
        )
        self.assert_status_progress_with_blocker(
            task_text,
            "self-e2e-unresolved:degraded-delivery:REQ-PA-DELIVERY:deferred",
        )

    def test_zero_issue_blocker_can_be_detected_from_evidence_when_summary_is_generic(self) -> None:
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            "[Candidates]\n"
            "selfe2e-depth: disposition=integrated; "
            "summary=SelfE2E finalization depth evidence complete; "
            "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
                "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
            "main-self-exit.json closed=true auxiliary_shell_panes same-session "
            "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n",
            (
                "[Candidates]\n"
                "round8-observation: disposition=deferred; "
                "summary=Round8 follow-up remains pending; "
                "evidence=degraded delivery requires later clean SelfE2E proof\n"
                "selfe2e-depth: disposition=integrated; "
                "summary=SelfE2E finalization depth evidence complete; "
                "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
                "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
                "main-self-exit.json closed=true auxiliary_shell_panes same-session "
                "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
            ),
        )
        self.assert_status_progress_with_blocker(
            task_text,
            "self-e2e-unresolved:degraded-delivery:round8-observation:deferred",
        )

    def test_approval_userneeded_cleanup_observation_blocks_zero_issue_done(self) -> None:
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            "[Candidates]\n"
            "selfe2e-depth: disposition=integrated; "
            "summary=SelfE2E finalization depth evidence complete; "
            "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
                "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
            "main-self-exit.json closed=true auxiliary_shell_panes same-session "
            "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n",
            (
                "[Candidates]\n"
                "service-observation: disposition=deferred; "
                "summary=ServiceE2E approval/UserNeeded/cleanup route still needs later clean proof; "
                "evidence=.tmp/self-improvement-e2e/service-observations.md\n"
                "selfe2e-depth: disposition=integrated; "
                "summary=SelfE2E finalization depth evidence complete; "
                "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
            "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
                "main-self-exit.json closed=true auxiliary_shell_panes same-session "
                "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
            ),
        )
        self.assert_status_progress_with_blocker(
            task_text,
            "self-e2e-unresolved:approval-userneeded-cleanup:service-observation:deferred",
        )

    def test_service_e2e_approval_replay_observation_blocks_zero_issue_done(self) -> None:
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            "[Candidates]\n"
            "selfe2e-depth: disposition=integrated; "
            "summary=SelfE2E finalization depth evidence complete; "
            "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
            "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
            "main-self-exit.json closed=true auxiliary_shell_panes same-session "
            "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n",
            (
                "[Candidates]\n"
                "service-replay: disposition=deferred; "
                "summary=ServiceE2E approval replay not yet proven through worker intake path; "
                "evidence=.tmp/self-improvement-e2e/service-replay.md\n"
                "selfe2e-depth: disposition=integrated; "
                "summary=SelfE2E finalization depth evidence complete; "
                "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
            "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
                "main-self-exit.json closed=true auxiliary_shell_panes same-session "
                "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
            ),
        )
        self.assert_status_progress_with_blocker(
            task_text,
            "self-e2e-unresolved:service-e2e-approval-replay:service-replay:deferred",
        )

    def test_missing_service_e2e_approval_replay_id_blocks_done(self) -> None:
        missing = SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS[0].defect_id
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            f"service-e2e-approval-replay-{missing}",
            "service-e2e-approval-replay-missing-from-ledger",
        )

        self.assert_status_progress_with_blocker(
            task_text,
            f"self-e2e-missing:service-approval-replay:{missing}",
        )

    def test_short_selfe2e_run_observation_blocks_zero_issue_done(self) -> None:
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            "[Candidates]\n"
            "selfe2e-depth: disposition=integrated; "
            "summary=SelfE2E finalization depth evidence complete; "
            "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
            "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
            "main-self-exit.json closed=true auxiliary_shell_panes same-session "
            "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n",
            (
                "[Candidates]\n"
                "short-run: disposition=deferred; "
                "summary=SelfE2E short run ended before improvement sweep replay and PA review proof; "
                "evidence=.tmp/self-improvement-e2e/run-duration.json\n"
                "selfe2e-depth: disposition=integrated; "
                "summary=SelfE2E finalization depth evidence complete; "
                "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
            "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
                "main-self-exit.json closed=true auxiliary_shell_panes same-session "
                "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
            ),
        )
        self.assert_status_progress_with_blocker(
            task_text,
            "self-e2e-unresolved:short-selfe2e-run:short-run:deferred",
        )

    def test_selfe2e_completing_in_minutes_observation_blocks_zero_issue_done(self) -> None:
        task_text = SELF_E2E_FINALIZED_TASK_FILE.replace(
            "[Candidates]\n"
            "selfe2e-depth: disposition=integrated; "
            "summary=SelfE2E finalization depth evidence complete; "
            "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
            "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
            "main-self-exit.json closed=true auxiliary_shell_panes same-session "
            "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n",
            (
                "[Candidates]\n"
                "minutes-run: disposition=deferred; "
                "summary=SelfE2E completing in minutes is itself a completion-contract defect; "
                "evidence=.tmp/self-improvement-e2e/run-duration.json\n"
                "selfe2e-depth: disposition=integrated; "
                "summary=SelfE2E finalization depth evidence complete; "
                "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
            "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
                "main-self-exit.json closed=true auxiliary_shell_panes same-session "
                "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
            ),
        )
        self.assert_status_progress_with_blocker(
            task_text,
            "self-e2e-unresolved:short-selfe2e-minutes:minutes-run:deferred",
        )

    def assert_status_progress_with_blocker(self, task_text: str, blocker: str) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
            task_file.write_text(task_text, encoding="utf-8")
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
