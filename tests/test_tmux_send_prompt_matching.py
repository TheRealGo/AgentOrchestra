from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendPromptMatchingTests(unittest.TestCase):
    def test_send_text_retries_when_long_message_composer_line_is_wrapped(self) -> None:
        message = (
            "MainAgent: You are pro-runtime. Please inspect SPEC.md and "
            "AgentOrchestra code for launch and tmux delivery risks."
        )
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: You are pro-runtime.   Please inspect SPEC.md and\n"
                "  AgentOrchestra code for launch and tmux delivery risks.\n",
                "› MainAgent: You are pro-runtime. Please inspect SPEC.md and\n\n• Working\n",
            ]
        )

        result = send_text("%8", message, runner=fake)

        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(len(send_key_calls), 3)

    def test_send_text_accepts_very_narrow_wrapped_prompt_when_agent_activity_follows(self) -> None:
        message = (
            "ProfessionalAgent pro-sre to pro-runtime: review Stop Hook tmux delivery "
            "confirmation for narrow panes before final operability signoff"
        )
        fake = FakeTmuxSend(
            captures=[
                "› ProfessionalAgent\n"
                "  pro-sre to\n"
                "  pro-runtime:\n"
                "  review Stop\n"
                "  Hook tmux\n"
                "  delivery\n"
                "  confirmation\n"
                "  for narrow\n"
                "  panes before\n"
                "  final\n"
                "  operability\n"
                "  signoff\n"
                "\n"
                "• Working\n",
            ]
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(send_key_calls), 2)

    def test_send_text_fails_when_probe_scrolled_out_and_only_prompt_tail_working_remains(self) -> None:
        message = "MainAgent: " + " ".join(f"token{i}" for i in range(30))
        queued_capture = "\n".join(
            [
                "› MainAgent: token0 token1 token2 token3 token4 token5",
                *(f"  continuation line {index}" for index in range(16)),
            ]
        )
        fake = FakeTmuxSend(captures=[queued_capture, "› MainAgent: token0 token1 token2\n\n• Working\n"])

        result = send_text("%8", message, runner=fake, poll_interval_seconds=0)

        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 3)
        self.assertEqual(len(send_key_calls), 4)

    def test_send_text_retries_when_message_visible_without_agent_activity(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "MainAgent: please review the final change set\n",
                "› MainAgent: please review the final change set\n\n• Working\n",
            ]
        )

        result = send_text(
            "%8",
            "MainAgent: please review the final change set",
            runner=fake,
            poll_interval_seconds=0,
        )

        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(len(send_key_calls), 3)

    def test_send_text_accepts_prompt_history_when_agent_activity_follows(self) -> None:
        message = "MainAgent: please review the final change set"
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: please review the final change set\n\n• Working\n",
            ]
        )

        result = send_text("%8", message, runner=fake, poll_interval_seconds=0)

        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(send_key_calls), 2)

    def test_send_text_does_not_accept_old_activity_before_visible_message(self) -> None:
        message = "MainAgent: please review the final change set"
        fake = FakeTmuxSend(
            captures=["• Working\n› MainAgent: please review the final change set\n\ntab to queue message\n"]
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_accepts_visible_message_only_when_new_activity_follows(self) -> None:
        message = "MainAgent: please review the final change set"
        fake = FakeTmuxSend(captures=["MainAgent: please review the final change set\nExplored\n"])

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_does_not_accept_start_marker_words_inside_queued_message(self) -> None:
        message = "MainAgent: mention Working while still queued"
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: mention Working while still queued\n"
                "  continuation says Explored and Ran commands\n"
            ]
        )

        result = send_text("%8", message, runner=fake, max_retries=0, poll_interval_seconds=0)

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)


if __name__ == "__main__":
    unittest.main()
