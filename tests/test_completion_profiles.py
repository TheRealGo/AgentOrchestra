from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.completion_profiles import (  # noqa: E402
    LOCAL_TWO_USER_PRODUCTION_LIKE,
    PUBLIC_RELEASE,
    SELF_IMPROVEMENT,
    classify_gate,
    infer_profile,
    service_defect_intake_items,
    status_for_gate,
)


class CompletionProfileTests(unittest.TestCase):
    def test_local_two_user_profile_defers_public_release_only_evidence(self) -> None:
        classification = classify_gate(LOCAL_TWO_USER_PRODUCTION_LIKE, "app_store")

        self.assertEqual(classification.disposition, "deferred")
        self.assertEqual(status_for_gate(classification), "not-applicable")
        self.assertIn("not a blocker", classification.rationale)

    def test_local_two_user_profile_keeps_local_evidence_blocking(self) -> None:
        for evidence_kind in ("local_safari", "iphone_safari", "direct_ios_install", "local_db_persistence"):
            with self.subTest(evidence_kind=evidence_kind):
                classification = classify_gate(LOCAL_TWO_USER_PRODUCTION_LIKE, evidence_kind)

                self.assertEqual(classification.disposition, "blocking")
                self.assertEqual(status_for_gate(classification), "open")

    def test_public_release_profile_keeps_public_evidence_blocking(self) -> None:
        classification = classify_gate(PUBLIC_RELEASE, "production_provider")

        self.assertEqual(classification.disposition, "blocking")
        self.assertEqual(status_for_gate(classification), "open")

    def test_user_intent_infers_completion_profile(self) -> None:
        self.assertEqual(
            infer_profile("first local two-person operation, public release deferred"),
            LOCAL_TWO_USER_PRODUCTION_LIKE,
            "deferred public release evidence must not override local-first intent",
        )
        self.assertEqual(infer_profile("ローカル2人運用を先に成立させる"), LOCAL_TWO_USER_PRODUCTION_LIKE)
        self.assertEqual(infer_profile("self-improvement E2E until zero issues"), SELF_IMPROVEMENT)

    def test_unknown_evidence_requires_explicit_classification(self) -> None:
        classification = classify_gate(LOCAL_TWO_USER_PRODUCTION_LIKE, "quantum_certification")

        self.assertEqual(classification.disposition, "needs-classification")
        self.assertEqual(status_for_gate(classification), "open")

    def test_service_e2e_defect_brief_maps_to_self_improvement_items(self) -> None:
        brief = """
        Service E2E exposed completion profile drift for local_two_user_production_like,
        task file duplicate sections and malformed gates, tmux composer residue and
        submit key delivery failures, approval/UserNeeded overuse, usage limit stale
        pane recovery gaps, and missing service E2E defect intake for self-improvement.
        """

        items = service_defect_intake_items(brief)

        self.assertIn("completion-profile-user-intent-gates", items)
        self.assertIn("task-file-finalization-validation", items)
        self.assertIn("tmux-delivery-confirmation", items)
        self.assertIn("approval-userneeded-classification", items)
        self.assertIn("usage-limit-pane-recovery", items)
        self.assertIn("service-e2e-defect-intake", items)


if __name__ == "__main__":
    unittest.main()
