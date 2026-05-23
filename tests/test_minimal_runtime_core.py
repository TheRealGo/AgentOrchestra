from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import ACTIVE_STATES, QUIET_STATES, AgentState  # noqa: E402
from agent_orchestra_minimal.task_file import ALLOWED_STATUS, OPEN_WORK_SECTIONS, SharedTaskFile  # noqa: E402


CANONICAL_EMPTY_TASK_FILE = """\
[status]
done

[Backlog]

[InProgress]

[InReview]

[Done]
completed item
"""


class SharedTaskFileParsingTests(unittest.TestCase):
    def test_shared_task_status_values_are_exactly_spec_values(self) -> None:
        self.assertEqual(ALLOWED_STATUS, {"progress", "done"})

    def test_parse_canonical_shared_task_file(self) -> None:
        task_file = SharedTaskFile.parse(
            """\
[status]
progress

[Backlog]
backlog item

[InProgress]
active item

[InReview]
review item

[Done]
done item
"""
        )

        self.assertEqual(task_file.status, "progress")
        self.assertEqual(task_file.sections["Backlog"], ["backlog item"])
        self.assertEqual(task_file.sections["InProgress"], ["active item"])
        self.assertEqual(task_file.sections["InReview"], ["review item"])
        self.assertEqual(task_file.sections["Done"], ["done item"])

    def test_rejects_status_outside_spec_allowed_values(self) -> None:
        with self.assertRaises(ValueError):
            SharedTaskFile.parse(
                """\
[status]
paused

[Backlog]

[InProgress]

[InReview]

[Done]
"""
            )

    def test_rejects_status_case_or_bullet_variants(self) -> None:
        for status in ("Done", "- done"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError, "invalid shared task status"):
                    SharedTaskFile.parse(
                        f"""\
[status]
{status}

[Backlog]

[InProgress]

[InReview]

[Done]
"""
                    )
    def test_rejects_content_before_first_section(self) -> None:
        with self.assertRaisesRegex(ValueError, "content must appear under a required section"):
            SharedTaskFile.parse(
                """\
scratch note

[status]
done

[Backlog]

[InProgress]

[InReview]

[Done]
"""
            )

    def test_rejects_missing_required_sections(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing required sections"):
            SharedTaskFile.parse(
                """\
[status]
done

[Backlog]
"""
            )

    def test_rejects_unknown_sections(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown shared task file section"):
            SharedTaskFile.parse(
                """\
[status]
done

[Backlog]

[InProgress]

[InReview]

[Done]

[Blocked]
deferred
"""
            )

    def test_rejects_duplicate_sections(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate shared task file section"):
            SharedTaskFile.parse(
                """\
[status]
done

[Backlog]

[InProgress]
active

[InProgress]
also active

[InReview]

[Done]
"""
            )

    def test_rejects_multiple_status_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one value"):
            SharedTaskFile.parse(
                """\
[status]
done
progress

[Backlog]

[InProgress]

[InReview]

[Done]
"""
            )


class SharedTaskFileOpenWorkTests(unittest.TestCase):
    def test_only_backlog_in_progress_and_in_review_are_open_work_sections(self) -> None:
        self.assertEqual(OPEN_WORK_SECTIONS, ("Backlog", "InProgress", "InReview"))

    def test_done_items_are_not_open_work(self) -> None:
        task_file = SharedTaskFile.parse(CANONICAL_EMPTY_TASK_FILE)

        self.assertFalse(task_file.has_open_work)

    def test_backlog_in_progress_and_in_review_are_open_work(self) -> None:
        for section_name in ("Backlog", "InProgress", "InReview"):
            with self.subTest(section=section_name):
                text = CANONICAL_EMPTY_TASK_FILE.replace(
                    f"[{section_name}]\n\n", f"[{section_name}]\nopen item\n\n"
                )
                task_file = SharedTaskFile.parse(text)

                self.assertTrue(task_file.has_open_work)


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

if __name__ == "__main__":
    unittest.main()
