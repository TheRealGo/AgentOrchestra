from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.rekick import decide_wake  # noqa: E402
from agent_orchestra_minimal.task_file import SharedTaskFile  # noqa: E402


CANONICAL_EMPTY_TASK_FILE = """\
[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]

[Done]
completed item
"""


class RekickDecisionTests(unittest.TestCase):
    def test_main_agent_rekicks_while_status_is_progress_even_without_open_work(
        self,
    ) -> None:
        task_file = SharedTaskFile.parse(
            CANONICAL_EMPTY_TASK_FILE.replace("[status]\ndone", "[status]\nprogress")
        )
        agent_state = AgentState.from_mapping(
            {"agent_kind": "main", "state": "done"}, default_agent_id="main"
        )

        self.assertTrue(decide_wake(task_file, agent_state).should_wake)

    def test_main_agent_rekicks_when_done_status_still_has_open_work(self) -> None:
        task_file = SharedTaskFile.parse(
            CANONICAL_EMPTY_TASK_FILE.replace("[InReview]\n\n", "[InReview]\nreview\n\n")
        )
        agent_state = AgentState.from_mapping(
            {"agent_kind": "main", "state": "done"}, default_agent_id="main"
        )

        self.assertTrue(decide_wake(task_file, agent_state).should_wake)

    def test_main_agent_stays_quiet_when_done_status_has_no_open_work(self) -> None:
        task_file = SharedTaskFile.parse(CANONICAL_EMPTY_TASK_FILE)
        agent_state = AgentState.from_mapping(
            {"agent_kind": "main", "state": "done"}, default_agent_id="main"
        )

        self.assertTrue(task_file.is_finalized)
        self.assertFalse(decide_wake(task_file, agent_state).should_wake)

    def test_main_agent_rekick_follows_task_file_finalization_contract(self) -> None:
        agent_state = AgentState.from_mapping(
            {"agent_kind": "main", "state": "done"}, default_agent_id="main"
        )
        task_files = (
            SharedTaskFile.parse(CANONICAL_EMPTY_TASK_FILE),
            SharedTaskFile.parse(
                CANONICAL_EMPTY_TASK_FILE.replace("[status]\ndone", "[status]\nprogress")
            ),
            SharedTaskFile.parse(
                CANONICAL_EMPTY_TASK_FILE.replace("[Backlog]\n\n", "[Backlog]\nnext-cycle\n\n")
            ),
            SharedTaskFile.parse(
                CANONICAL_EMPTY_TASK_FILE.replace(
                    "[Candidates]\n\n",
                    "[Candidates]\ncandidate-1: disposition=open; summary=next cycle; evidence=review\n\n",
                )
            ),
        )

        for task_file in task_files:
            with self.subTest(blockers=task_file.finalization_blockers):
                self.assertEqual(
                    decide_wake(task_file, agent_state).should_wake,
                    not task_file.is_finalized,
                )

    def test_main_agent_rekicks_when_done_status_has_unresolved_candidates(self) -> None:
        task_file = SharedTaskFile.parse(
            CANONICAL_EMPTY_TASK_FILE.replace(
                "[Candidates]\n\n",
                "[Candidates]\ncandidate-1: disposition=open; summary=send retry helper\n\n",
            )
        )
        agent_state = AgentState.from_mapping(
            {"agent_kind": "main", "state": "done"}, default_agent_id="main"
        )

        decision = decide_wake(task_file, agent_state)

        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_done_with_unresolved_candidates")

    def test_professional_agent_rekicks_only_for_active_states(self) -> None:
        task_file = SharedTaskFile.parse(CANONICAL_EMPTY_TASK_FILE)

        for state in ("working", "progress", "ready"):
            with self.subTest(state=state):
                agent_state = AgentState.from_mapping({"state": f"{state}\n"})

                self.assertTrue(decide_wake(task_file, agent_state).should_wake)

        for state in (
            "ready_for_review",
            "done",
            "needs_user",
            "blocked",
            "rate_limited",
            "retired",
        ):
            with self.subTest(state=state):
                agent_state = AgentState.from_mapping({"state": f"{state}\n"})

                self.assertFalse(decide_wake(task_file, agent_state).should_wake)


if __name__ == "__main__":
    unittest.main()
