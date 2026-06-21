from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.self_exit import run_self_exit  # noqa: E402
from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from test_self_exit import FakeSelfExitTmux  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class SubmitKeyFallbackTests(unittest.TestCase):
    def test_send_text_falls_back_to_control_m_for_nonstandard_submit_key(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: investigate\n",
                "› MainAgent: investigate\n",
                "› MainAgent: investigate\n\nWorking\n",
            ]
        )

        result = send_text(
            "%7",
            "MainAgent: investigate",
            submit_key="M-Enter",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=1,
            max_retries=1,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertIn((["tmux", "send-keys", "-t", "%7", "M-Enter"], None), fake.calls)
        self.assertIn((["tmux", "send-keys", "-t", "%7", "C-m"], None), fake.calls)

    def test_run_self_exit_falls_back_to_control_m_for_nonstandard_submit_key(self) -> None:
        fake = FakeSelfExitTmux(closes_after_sends=2)

        result = run_self_exit(
            "%9",
            submit_key="M-Enter",
            runner=fake,
            sleeper=lambda _: None,
            attempts=3,
            delay_seconds=0,
        )

        self.assertTrue(result.closed)
        self.assertEqual(result.attempts, 2)
        exit_sends = [call for call in fake.calls if call[:2] == ["tmux", "send-keys"] and "/exit" in call]
        self.assertEqual(exit_sends[0][-1], "M-Enter")
        self.assertEqual(exit_sends[1][-1], "C-m")


if __name__ == "__main__":
    unittest.main()
