from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import ACTIVE_STATES, QUIET_STATES, AgentState  # noqa: E402


class ProfessionalAgentStateTests(unittest.TestCase):
    def test_agent_state_sets_match_stop_hook_contract(self) -> None:
        self.assertEqual(ACTIVE_STATES, {"working", "progress", "ready"})
        self.assertEqual(
            QUIET_STATES,
            {
                "ready_for_review",
                "done",
                "needs_user",
                "blocked",
                "rate_limited",
                "retired",
            },
        )

    def test_active_professional_states_indicate_unfinished_work(self) -> None:
        for state in ("working", "progress", "ready"):
            with self.subTest(state=state):
                agent_state = AgentState.from_mapping({"state": f" {state}\n"})

                self.assertTrue(agent_state.is_active)
                self.assertFalse(agent_state.is_quiet)

    def test_quiet_professional_states_do_not_indicate_unfinished_work(self) -> None:
        for state in (
            "ready_for_review",
            "done",
            "needs_user",
            "blocked",
            "rate_limited",
            "retired",
        ):
            with self.subTest(state=state):
                agent_state = AgentState.from_mapping({"state": f" {state}\n"})

                self.assertTrue(agent_state.is_quiet)
                self.assertFalse(agent_state.is_active)

    def test_agent_kind_is_normalized_for_deterministic_stop_hook_identity(self) -> None:
        main_state = AgentState.from_mapping({"state": "working", "agent_kind": " main_agent "})
        professional_state = AgentState.from_mapping(
            {"state": "working", "agent_kind": " professional "}
        )

        self.assertEqual(main_state.agent_kind, "MainAgent")
        self.assertTrue(main_state.is_main)
        self.assertEqual(professional_state.agent_kind, "ProfessionalAgent")
        self.assertFalse(professional_state.is_main)

    def test_agent_kind_alias_is_normalized_from_structured_kind_field(self) -> None:
        agent_state = AgentState.from_mapping({"state": "working", "kind": "main"})

        self.assertEqual(agent_state.agent_kind, "MainAgent")
        self.assertTrue(agent_state.is_main)

    def test_default_agent_kind_recovers_legacy_simple_state_identity(self) -> None:
        agent_state = AgentState.parse("working\n", default_agent_kind="MainAgent")

        self.assertEqual(agent_state.agent_kind, "MainAgent")
        self.assertTrue(agent_state.is_main)

    def test_default_agent_kind_recovers_structured_state_without_kind(self) -> None:
        agent_state = AgentState.from_mapping(
            {"state": "working"},
            default_agent_kind="MainAgent",
        )

        self.assertEqual(agent_state.agent_kind, "MainAgent")
        self.assertTrue(agent_state.is_main)

    def test_direct_constructor_normalizes_agent_kind_aliases(self) -> None:
        agent_state = AgentState(state="working", agent_kind=" main ")

        self.assertEqual(agent_state.agent_kind, "MainAgent")
        self.assertTrue(agent_state.is_main)

    def test_agent_kind_rejects_unknown_values_in_structured_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid agent kind"):
            AgentState.from_mapping({"state": "working", "agent_kind": "Main Agent"})

    def test_invalid_state_tmux_target_metadata_does_not_invalidate_agent_state(self) -> None:
        agent_state = AgentState.from_mapping(
            {
                "state": "ready_for_review",
                "agent_kind": "ProfessionalAgent",
                "tmux_target": ":0.1",
            }
        )

        self.assertTrue(agent_state.is_quiet)
        self.assertIsNone(agent_state.tmux_target)


if __name__ == "__main__":
    unittest.main()
