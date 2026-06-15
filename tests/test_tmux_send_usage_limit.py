from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendUsageLimitTests(unittest.TestCase):
    def test_send_text_does_not_paste_into_usage_limited_pane(self) -> None:
        fake = FakeTmuxSend(
            captures=[],
            baseline_capture=(
                "■ You've hit your usage limit. Visit\n"
                "https://chatgpt.com/codex/settings/usage\n\n"
                "› Improve documentation in @filename\n\n"
                "  Goal hit usage limits (/goal resume)\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent: recover and finish the E2E ledger",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        paste_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "paste-buffer"]]
        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)
        self.assertEqual(paste_calls, [])


if __name__ == "__main__":
    unittest.main()
