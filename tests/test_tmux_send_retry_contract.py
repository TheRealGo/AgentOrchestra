from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendRetryContractTests(unittest.TestCase):
    def test_send_text_accepts_on_final_configured_retry_attempt(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› ProfessionalAgent: please review the contract\n",
                "› ProfessionalAgent: please review the contract\n",
                "› ProfessionalAgent: please review the contract\n\n• Working\n",
            ]
        )

        result = send_text(
            "%8",
            "ProfessionalAgent: please review the contract",
            runner=fake,
            max_retries=2,
        )

        send_key_calls = [
            call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"] and "-l" not in call[0]
        ]
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(len(send_key_calls), 3)

    def test_send_text_accepts_new_work_even_when_default_prompt_remains_visible(self) -> None:
        text = (
            "MainAgent: You are ProfessionalAgent pa-runtime. "
            "Keep .tmp/self-improvement-e2e/status as progress while any issue remains."
        )
        fake = FakeTmuxSend(
            captures=[
                (
                    "› Find and fix a bug in @filename\n\n"
                    "› MainAgent: You are ProfessionalAgent pa-runtime.\n"
                    "  Keep .tmp/self-improvement-e2e/status as progress while any issue remains.\n\n"
                    "• I'll update my state to working before review.\n"
                    "• Working (30s • esc to interrupt)\n\n"
                    "› Find and fix a bug in @filename\n"
                    "  tab to queue message\n"
                ),
                (
                    "› Find and fix a bug in @filename\n\n"
                    "› MainAgent: You are ProfessionalAgent pa-runtime.\n"
                    "  Keep .tmp/self-improvement-e2e/status as progress while any issue remains.\n\n"
                    "• I'll update my state to working before review.\n"
                    "• Working (30s • esc to interrupt)\n\n"
                    "› Find and fix a bug in @filename\n"
                    "  tab to queue message\n"
                )
            ],
            baseline_capture="› Find and fix a bug in @filename\n",
        )

        result = send_text(
            "%8",
            text,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_still_rejects_queue_marker_before_work_starts(self) -> None:
        text = "MainAgent: please review the completion gate"
        fake = FakeTmuxSend(
            captures=[
                (
                    "› MainAgent: please review the completion gate\n\n"
                    "  tab to queue message\n\n"
                    "• Working (30s • esc to interrupt)\n"
                )
            ],
            baseline_capture="› Find and fix a bug in @filename\n",
        )

        result = send_text(
            "%8",
            text,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)


if __name__ == "__main__":
    unittest.main()
