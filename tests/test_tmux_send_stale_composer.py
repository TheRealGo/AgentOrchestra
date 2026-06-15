from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend, tmux_buffer_name  # noqa: E402


class TmuxSendStaleComposerTests(unittest.TestCase):
    def test_send_text_clears_nondefault_stale_composer_prompt_before_paste(self) -> None:
        fake = FakeTmuxSend(
            captures=["› MainAgent: fresh assignment\n\n• Working\n"],
            baseline_capture="› commands, blocking_objection=...\n",
        )

        result = send_text("%7", "MainAgent: fresh assignment", runner=fake)

        buffer_name = tmux_buffer_name(fake)
        self.assertTrue(result.accepted)
        self.assertEqual(
            fake.calls[:5],
            [
                (["tmux", "load-buffer", "-b", buffer_name, "-"], "MainAgent: fresh assignment"),
                (["tmux", "capture-pane", "-t", "%7", "-p", "-S", "-120"], None),
                (["tmux", "send-keys", "-t", "%7", "Escape", "C-u"], None),
                (["tmux", "capture-pane", "-t", "%7", "-p", "-S", "-120"], None),
                (["tmux", "paste-buffer", "-t", "%7", "-b", buffer_name], None),
            ],
        )


if __name__ == "__main__":
    unittest.main()
