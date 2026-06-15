from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendProbeAbsentTests(unittest.TestCase):
    def test_accepts_same_default_prompt_when_new_work_starts_without_visible_probe(self) -> None:
        message = "MainAgent: " + " ".join(f"assignment-token-{index}" for index in range(80))
        fake = FakeTmuxSend(
            captures=["› Find and fix a bug in @filename\n\n• Working\n"],
            baseline_capture="› Find and fix a bug in @filename\n",
        )

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_does_not_paste_into_agent_message_prompt_with_no_visible_probe(self) -> None:
        message = "MainAgent: " + " ".join(f"assignment-token-{index}" for index in range(80))
        fake = FakeTmuxSend(
            captures=["› MainAgent: stale queued message\n\n• Working\n"],
            baseline_capture="› MainAgent: stale queued message\n",
        )

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)
        self.assertFalse(fake.paste_seen)


if __name__ == "__main__":
    unittest.main()
