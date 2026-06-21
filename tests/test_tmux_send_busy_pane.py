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

    def test_send_text_rejects_goal_blocked_pane_as_not_ready(self) -> None:
        fake = FakeTmuxSend(
            captures=[],
            baseline_capture=(
                "› Runtime wake received; continue unresolved gates.\n\n"
                "gpt-5.5 default · /workspace  Goal blocked (/goal resume)\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent -> pro-qa: resume unresolved completion gates",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)

    def test_send_text_ignores_goal_blocked_mentions_in_prior_report(self) -> None:
        fake = FakeTmuxSend(
            captures=["› MainAgent: review\n\n• Working\n"],
            baseline_capture=(
                "• Prior report: Goal blocked (/goal resume) was reviewed.\n\n"
                "─ Worked for 1m 00s ─────────────\n\n"
                "› Improve documentation in @filename\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent: review",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_can_send_explicit_interrupted_recovery(self) -> None:
        fake = FakeTmuxSend(
            captures=["› MainAgent: resume from interrupted approval\n\n• Working\n"],
            baseline_capture=(
                "■ Conversation interrupted - tell the model what to do differently.\n\n"
                "› Write tests for @filename\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent: resume from interrupted approval",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
            allow_interrupted_recovery=True,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)


if __name__ == "__main__":
    unittest.main()
