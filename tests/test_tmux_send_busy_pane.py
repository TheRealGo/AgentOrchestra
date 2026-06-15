from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendBusyPaneTests(unittest.TestCase):
    def test_send_text_rejects_background_terminal_pane_as_not_ready(self) -> None:
        fake = FakeTmuxSend(
            captures=[],
            baseline_capture=(
                "• Working (14m 21s • esc to interrupt) · 1 background terminal running · /ps to view\n\n"
                "› Find and fix a bug in @filename\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent -> pro-qa: close visual retries and report evidence",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)

    def test_send_text_rejects_interrupted_goal_paused_pane_as_not_ready(self) -> None:
        fake = FakeTmuxSend(
            captures=[],
            baseline_capture=(
                "■ Conversation interrupted - tell the model what to do differently.\n\n"
                "› Current E2E cycle has enough evidence; please close.\n\n"
                "gpt-5.5 default · /workspace  Goal paused (/goal resume)\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent -> pro-qa: close visual retries and report evidence",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)


if __name__ == "__main__":
    unittest.main()
