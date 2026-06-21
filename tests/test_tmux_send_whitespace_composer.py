from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendWhitespaceComposerTests(unittest.TestCase):
    def test_send_text_clears_whitespace_only_composer_before_pasting(self) -> None:
        fake = FakeTmuxSend(
            captures=["› MainAgent: investigate\n\n• Working\n"],
            baseline_capture="› \n\n\n\n",
        )

        result = send_text("%7", "MainAgent: investigate", runner=fake)

        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertTrue(result.accepted)
        self.assertIn((["tmux", "send-keys", "-t", "%7", "Escape", "C-u"], None), send_key_calls)


if __name__ == "__main__":
    unittest.main()
