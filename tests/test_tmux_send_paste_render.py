from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendPasteRenderTests(unittest.TestCase):
    def test_send_text_waits_for_pasted_probe_before_first_submit(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› \n",
                "› MainAgent: investigate paste render race\n",
                "› MainAgent: investigate paste render race\n\n• Working\n",
            ],
        )

        result = send_text(
            "%8",
            "MainAgent: investigate paste render race",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=5,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        paste_index = next(index for index, call in enumerate(fake.calls) if call[0][:2] == ["tmux", "paste-buffer"])
        first_submit_index = next(
            index
            for index, call in enumerate(fake.calls[paste_index + 1 :], paste_index + 1)
            if call[0][:2] == ["tmux", "send-keys"] and "-l" not in call[0]
        )
        self.assertTrue(
            any(call[0][:2] == ["tmux", "capture-pane"] for call in fake.calls[paste_index + 1 : first_submit_index])
        )

    def test_send_text_waits_beyond_five_captures_when_paste_render_is_slow(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› \n",
                "› \n",
                "› \n",
                "› \n",
                "› \n",
                "› MainAgent: investigate slow paste render\n",
                "› MainAgent: investigate slow paste render\n\n• Working\n",
            ],
        )

        result = send_text(
            "%8",
            "MainAgent: investigate slow paste render",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=8,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        paste_index = next(index for index, call in enumerate(fake.calls) if call[0][:2] == ["tmux", "paste-buffer"])
        first_submit_index = next(
            index
            for index, call in enumerate(fake.calls[paste_index + 1 :], paste_index + 1)
            if call[0][:2] == ["tmux", "send-keys"] and "-l" not in call[0]
        )
        captures_before_submit = [
            call for call in fake.calls[paste_index + 1 : first_submit_index] if call[0][:2] == ["tmux", "capture-pane"]
        ]
        self.assertGreaterEqual(len(captures_before_submit), 6)

    def test_first_submit_uses_post_submit_capture_not_paste_capture(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: verify default C-m delivery\n",
                "› MainAgent: verify default C-m delivery\n\n• Working\n",
            ],
        )

        result = send_text(
            "%8",
            "MainAgent: verify default C-m delivery",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=1,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        submit_calls = [
            call
            for call in fake.calls
            if call[0][:2] == ["tmux", "send-keys"] and "-l" not in call[0] and call[0][-2:] != ["Escape", "C-u"]
        ]
        self.assertEqual(len(submit_calls), 1)
        self.assertEqual(submit_calls[0][0][-1], "C-m")


if __name__ == "__main__":
    unittest.main()
