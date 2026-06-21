from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.user_needed import classify_intervention  # noqa: E402
from agent_orchestra_minimal.autonomy_policy import (  # noqa: E402
    autonomy_policy_diagnostic_lines,
    classify_action,
    classify_docker_cleanup,
    classify_process_cleanup,
    classify_service_e2e_approval_replay,
    classify_service_e2e_approval_prompt,
)


class UserNeededClassificationTests(unittest.TestCase):
    def test_low_risk_in_scope_approval_prompt_is_autonomy_blocker_not_needs_user(self) -> None:
        result = classify_intervention(
            reason="codex approval prompt",
            in_edit_root=True,
            low_risk=True,
        )

        self.assertEqual(result.disposition, "autonomy_blocker")
        self.assertEqual(result.ledger_status, "open")
        self.assertTrue(result.zero_issue_blocker)
        self.assertIn("unresolved SelfE2E issue", result.rationale)

    def test_external_credential_request_is_true_needs_user(self) -> None:
        result = classify_intervention(
            reason="credential",
            in_edit_root=True,
            low_risk=True,
        )

        self.assertEqual(result.disposition, "needs_user")
        self.assertEqual(result.ledger_status, "needs_user")
        self.assertTrue(result.zero_issue_blocker)

    def test_destructive_irreversible_reason_matches_action_policy_boundary(self) -> None:
        result = classify_intervention(
            reason="destructive irreversible",
            in_edit_root=True,
            low_risk=True,
        )

        self.assertEqual(result.disposition, "needs_user")
        self.assertEqual(result.ledger_status, "needs_user")
        self.assertTrue(result.zero_issue_blocker)

    def test_action_policy_keeps_low_risk_approval_prompt_open(self) -> None:
        result = classify_action("test file edit", approval_prompt_seen=True)

        self.assertEqual(result.category, "autonomy_defect")
        self.assertEqual(result.ledger_status, "open")
        self.assertIn("SelfE2E issue", result.rationale)

    def test_action_policy_marks_public_release_approval_as_true_user_needed(self) -> None:
        result = classify_action("production public release approval")

        self.assertEqual(result.category, "true_user_needed")
        self.assertEqual(result.ledger_status, "needs_user")

    def test_browser_verification_reruns_are_autonomous_without_approval_prompt(self) -> None:
        for action in ("browser evidence rerun", "local browser verification", "chromium firefox matrix"):
            with self.subTest(action=action):
                result = classify_action(action)

                self.assertEqual(result.category, "agent_autonomous")
                self.assertEqual(result.ledger_status, "satisfied")

    def test_local_ios_and_simulator_verification_reruns_are_autonomous(self) -> None:
        for action in (
            "local simulator verification",
            "ios simulator smoke",
            "ios build smoke",
            "mobile route evidence",
            "mobile interactive evidence",
        ):
            with self.subTest(action=action):
                result = classify_action(action)

                self.assertEqual(result.category, "agent_autonomous")
                self.assertEqual(result.ledger_status, "satisfied")

    def test_local_verification_prompt_is_autonomy_defect_not_user_needed(self) -> None:
        for action in ("browser evidence rerun", "ios simulator smoke"):
            with self.subTest(action=action):
                result = classify_action(action, approval_prompt_seen=True)

                self.assertEqual(result.category, "autonomy_defect")
                self.assertEqual(result.ledger_status, "open")

    def test_run_scoped_process_cleanup_requires_identity_and_run_or_port_ownership(self) -> None:
        allowed = classify_process_cleanup(process_identity_known=True, run_owned=True)

        self.assertTrue(allowed.allowed)
        self.assertEqual(allowed.category, "run_scoped_cleanup")
        self.assertEqual(allowed.ledger_status, "satisfied")

        unknown_process = classify_process_cleanup(process_identity_known=False, run_owned=True, port_owned=True)
        unowned_process = classify_process_cleanup(process_identity_known=True)

        for result in (unknown_process, unowned_process):
            self.assertFalse(result.allowed)
            self.assertEqual(result.ledger_status, "blocked")

    def test_run_scoped_docker_cleanup_requires_current_run_scope(self) -> None:
        volume = classify_docker_cleanup(
            resource_type="volume",
            resource_name="agent_orchestra_20260621_postgres_data",
            current_run_scope="agent_orchestra_20260621",
        )
        container = classify_docker_cleanup(
            resource_type="container",
            resource_name="postgres",
            current_run_scope="agent_orchestra_20260621",
            compose_project="agent_orchestra_20260621",
        )

        for result in (volume, container):
            self.assertTrue(result.allowed)
            self.assertEqual(result.category, "run_scoped_cleanup")
            self.assertEqual(result.ledger_status, "satisfied")

    def test_non_run_scoped_docker_cleanup_blocks(self) -> None:
        result = classify_docker_cleanup(
            resource_type="volume",
            resource_name="too_restore_e2e_20260621_too_restore_postgres_data",
            current_run_scope="agent_orchestra_20260621",
            compose_project="too_restore_e2e_20260621",
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.category, "requires_user_needed_or_blocked")
        self.assertEqual(result.ledger_status, "blocked")

    def test_service_run_scoped_volume_cleanup_is_allowed_by_matching_scope(self) -> None:
        result = classify_docker_cleanup(
            resource_type="volume",
            resource_name="too_restore_e2e_20260621_too_restore_postgres_data",
            current_run_scope="too_restore_e2e_20260621",
        )

        self.assertTrue(result.allowed)
        self.assertEqual(result.category, "run_scoped_cleanup")

    def test_autonomy_policy_diagnostic_surfaces_required_classifications(self) -> None:
        output = "\n".join(autonomy_policy_diagnostic_lines())

        self.assertIn("browser_evidence_rerun", output)
        self.assertIn("ios_simulator_smoke", output)
        self.assertIn("cleanup docker_volume", output)
        self.assertIn("category=true_user_needed", output)

    def test_service_e2e_approval_stop_replay_classifies_all_nine_observations(self) -> None:
        replay = classify_service_e2e_approval_replay()

        self.assertEqual(len(replay), 9)
        for observation, result in replay:
            with self.subTest(command=observation.command):
                direct = classify_service_e2e_approval_prompt(
                    observation.command,
                    current_run_scope=observation.current_run_scope,
                    process_identity_known=observation.process_identity_known,
                    port_owned=observation.port_owned,
                )

                self.assertEqual(result.category, observation.expected_category)
                self.assertEqual(direct.category, observation.expected_category)
                self.assertEqual(result.ledger_status, "satisfied")

    def test_service_e2e_approval_prompt_uses_policy_path_in_user_needed_classifier(self) -> None:
        result = classify_intervention(
            reason="codex approval prompt",
            in_edit_root=True,
            low_risk=False,
            command="PLAYWRIGHT_PORT=3227 pnpm test:browser",
            current_run_scope="too_restore_e2e_20260621",
        )

        self.assertEqual(result.disposition, "autonomy_blocker")
        self.assertEqual(result.ledger_status, "open")
        self.assertIn("autonomy_policy", result.rationale)

    def test_service_e2e_approval_stops_route_all_nine_through_user_needed_classifier(self) -> None:
        replay = classify_service_e2e_approval_replay()

        self.assertEqual(len(replay), 9)
        for observation, _ in replay:
            with self.subTest(command=observation.command):
                result = classify_intervention(
                    reason="codex approval prompt",
                    in_edit_root=True,
                    low_risk=False,
                    command=observation.command,
                    current_run_scope=observation.current_run_scope,
                    process_identity_known=observation.process_identity_known,
                    port_owned=observation.port_owned,
                )

                self.assertEqual(result.disposition, "autonomy_blocker")
                self.assertEqual(result.ledger_status, "open")
                self.assertTrue(result.zero_issue_blocker)
                self.assertIn("autonomy_policy", result.rationale)

    def test_true_external_action_stays_needs_user_even_with_service_command_context(self) -> None:
        result = classify_intervention(
            reason="credential",
            in_edit_root=True,
            low_risk=True,
            command="pnpm test:browser",
            current_run_scope="too_restore_e2e_20260621",
        )

        self.assertEqual(result.disposition, "needs_user")
        self.assertEqual(result.ledger_status, "needs_user")
        self.assertTrue(result.zero_issue_blocker)


if __name__ == "__main__":
    unittest.main()
