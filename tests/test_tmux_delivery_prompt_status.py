from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxDeliveryPromptStatusTests(unittest.TestCase):
    def test_does_not_accept_prompt_tail_working_when_probe_scrolled_out(self) -> None:
        fake = FakeTmuxSend(captures=["› previous prompt\n\ngpt-5.5 default\n• Working\n"])

        result = send_text(
            "%8",
            "MainAgent: long assignment whose first-line probe has scrolled out",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_does_not_accept_indented_working_word_inside_prompt_tail(self) -> None:
        fake = FakeTmuxSend(captures=["› previous prompt\n\n  Working appears in wrapped text\n"])

        result = send_text(
            "%8",
            "MainAgent: long assignment whose first-line probe has scrolled out",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_does_not_accept_stale_activity_without_message_or_prompt(self) -> None:
        fake = FakeTmuxSend(captures=["• Working\nRan python3 -m unittest discover -s tests\n"])

        result = send_text(
            "%8",
            "ProfessionalAgent pro-runtime: please review runtime delivery",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_does_not_accept_unrelated_new_prompt_and_activity_without_probe(self) -> None:
        message = (
            "MainAgent: final report request for runtime round7 delivery probe "
            "with a unique token that is not visible"
        )
        fake = FakeTmuxSend(
            captures=[
                "› Find and fix a bug in @filename\n\n"
                "• Edited unrelated.py (+1 -1)\n\n"
                "› commands, blocking_objection=<none>\n\n"
                "• Working\n",
            ],
            baseline_capture="› Find and fix a bug in @filename\n",
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_new_activity_after_assignment_probe_scrolls_out(self) -> None:
        message = (
            "MainAgent -> pa-requirements-04: Audit requirement coverage and "
            "report blocking objections."
        )
        fake = FakeTmuxSend(
            captures=[
                "• I'll handle this as the Layer 04 requirements audit.\n\n"
                "• Edited /run/tasks.ini (+1 -1)\n\n"
                "• Working\n\n"
                "› Run /review on my current changes\n",
            ],
            baseline_capture="› Run /review on my current changes\n",
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_using_skill_activity_after_probe_scrolls_out(self) -> None:
        message = "MainAgent -> pro-qa-15: SelfE2E QA/runtime completion review assignment"
        fake = FakeTmuxSend(
            captures=[
                "• Using agent-orchestra-task-file first\n\n"
                "• Explored\n"
                "  └ Read SPEC.md\n",
            ],
            baseline_capture="› \n",
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_does_not_accept_using_acknowledgement_without_substantive_activity(self) -> None:
        message = "MainAgent -> pro-qa-15: SelfE2E QA/runtime completion review assignment"
        fake = FakeTmuxSend(
            captures=["• Using agent-orchestra-task-file first\n"],
            baseline_capture="› \n",
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_repeated_fresh_activity_line_after_acknowledgement(self) -> None:
        message = "MainAgent -> pro-runtime: re-check delivery confirmation edge cases"
        baseline = (
            "• Ran python3 -m unittest tests.test_tmux_delivery_prompt_status\n"
            "› Run /review on my current changes\n"
        )
        capture = (
            baseline
            + "• Using agent-orchestra-task-file first\n"
            + "• Ran python3 -m unittest tests.test_tmux_delivery_prompt_status\n"
        )
        fake = FakeTmuxSend(captures=[capture], baseline_capture=baseline)

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_wrapped_visible_message_when_activity_follows(self) -> None:
        message = (
            "MainAgent: You are pro-runtime. Please inspect SPEC.md and "
            "AgentOrchestra code for launch and tmux delivery risks."
        )
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: You are pro-runtime. Please inspect SPEC.md and\n"
                "  AgentOrchestra code for launch and tmux delivery risks.\n\n"
                "• Working\n"
            ]
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_long_agent_prompt_started_even_when_probe_tail_scrolled_out(self) -> None:
        message = (
            "MainAgent -> pro-ui: Review the AgenticRAG visual gate evidence and "
            "raise any blocking objection before finalization."
        )
        capture = (
            "› MainAgent -> pro-ui: Review the AgenticRAG visual gate evidence\n\n"
            "• Working\n"
        )
        fake = FakeTmuxSend(captures=[capture], baseline_capture="› Find and fix a bug in @filename\n")

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_started_assignment_when_next_composer_can_queue_followup(self) -> None:
        message = (
            "MainAgent -> pro-requirements: Review self-improvement requirements, "
            "edit-boundary evidence, and task ledger finalization contracts."
        )
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent -> pro-requirements: Review self-improvement\n"
                "  requirements, edit-boundary evidence, and task ledger\n"
                "  finalization contracts.\n\n"
                "• I’ll inspect the requested contracts first.\n\n"
                "• Working\n\n"
                "›\n"
                "  tab to queue message\n",
            ],
            baseline_capture="› Run /review on my current changes\n",
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_started_assignment_before_summarize_commits_default_prompt(self) -> None:
        message = (
            "MainAgent: You are qa-pa-round7 (Layer 15 QA/release). Target project "
            "is ${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra."
        )
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: You are qa-pa-round7 (Layer 15 QA/release). Target project\n"
                "  is ${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra.\n\n"
                "• I’ll take the QA/release scope and read the Round7 evidence first.\n\n"
                "• Working\n\n"
                "› Summarize recent commits\n\n"
                "  gpt-5.5 default · ${HOME}/Library/Application Support/agent-orchestr…\n",
            ],
            baseline_capture="› Summarize recent commits\n",
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_does_not_accept_stale_message_with_same_short_prefix(self) -> None:
        message = "MainAgent: please review the final-new change set for candidate delivery-probe"
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: please review the final-old change set for candidate "
                "delivery-probe\n\n• Working\n",
            ]
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_does_not_treat_indented_queue_marker_as_wrapped_message(self) -> None:
        message = "MainAgent: please review the final change set"
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: please review the final change set\n"
                "  tab to queue message\n\n"
                "• Working\n"
            ]
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_accepts_wrapped_cjk_message_when_activity_follows(self) -> None:
        message = (
            "SPEC.md を見て AgentOrchestra/ を改善してください。改善点がなくなるまで"
            "改善し続けてください。完了したら /exit でorchestraから抜けてください。"
        )
        fake = FakeTmuxSend(
            captures=[
                "› SPEC.md を見て AgentOrchestra/ を改善してください。改善点がなく\n"
                "  なるまで改善し続けてください。完了したら /exit でorchestraから\n"
                "  抜けてください。\n\n"
                "• Working\n"
            ]
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)


if __name__ == "__main__":
    unittest.main()
