from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend, delivery_input_calls  # noqa: E402


class TmuxSendStaleComposerTests(unittest.TestCase):
    def test_send_text_clears_nondefault_stale_composer_prompt_before_paste(self) -> None:
        fake = FakeTmuxSend(
            captures=["› MainAgent: fresh assignment\n\n• Working\n"],
            baseline_capture="› commands, blocking_objection=...\n",
        )

        result = send_text("%7", "MainAgent: fresh assignment", runner=fake)

        self.assertTrue(result.accepted)
        self.assertIn((["tmux", "send-keys", "-t", "%7", "Escape", "C-u"], None), fake.calls)
        self.assertEqual(delivery_input_calls(fake), [(["tmux", "paste-buffer", "-t", "%7", "-b", "agent-orchestra-msg-7"], None)])
        self.assertIn((["tmux", "load-buffer", "-b", "agent-orchestra-msg-7", "-"], "MainAgent: fresh assignment"), fake.calls)

    def test_send_text_treats_separator_before_default_prompt_as_ready(self) -> None:
        fake = FakeTmuxSend(
            captures=["› ProfessionalAgent: consult now\n\n• Working\n"],
            baseline_capture=(
                "• Ran python3 -m unittest discover -s tests\n  └ OK\n\n"
                "────────────────────────────────────────\n\n"
                "› Improve documentation in @filename\n\n"
                "  gpt-5.5 default · /Users/example/workspace\n"
            ),
        )

        result = send_text("%8", "ProfessionalAgent: consult now", runner=fake, poll_interval_seconds=0)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(delivery_input_calls(fake)), 1)


if __name__ == "__main__":
    unittest.main()
