from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendChoiceMenuTests(unittest.TestCase):
    def test_send_text_closes_model_selection_menu_before_pasting(self) -> None:
        baseline = [
            (
                "› 1. Switch to gpt-5.4-… Small, fast,\n"
                "                         and cost-\n"
                "                         efficient\n\n"
                "  Press enter to confirm or esc to go back\n"
            ),
            "› Improve documentation in @filename\n",
        ]
        fake = FakeTmuxSend(
            captures=["› MainAgent -> pro-runtime: final review request\n\n• Working\n"],
            baseline_capture=baseline,
        )

        result = send_text(
            "%8",
            "MainAgent -> pro-runtime: final review request",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertIn((["tmux", "send-keys", "-t", "%8", "Escape"], None), fake.calls)


if __name__ == "__main__":
    unittest.main()
