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
