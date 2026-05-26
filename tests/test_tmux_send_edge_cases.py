from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxSendEdgeCaseTests(unittest.TestCase):
    def test_send_text_does_not_accept_stale_activity_before_prompt_marker_without_probe(self) -> None:
        fake = FakeTmuxSend(captures=["• Working\n› unrelated prompt history\n"])

        result = send_text(
            "%8",
            "MainAgent: please review the final change set",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_does_not_accept_activity_after_unrelated_prompt_without_probe(self) -> None:
        fake = FakeTmuxSend(captures=["› unrelated prompt history\n\nExplored\n"])

        result = send_text(
            "%8",
            "MainAgent: please review the final change set",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_accepts_new_prompt_activity_when_long_wrapped_probe_does_not_match(self) -> None:
        message = (
            "MainAgent: You are pro-backend-runtime. Current user goal: read SPEC.md "
            "and improve AgentOrchestra until no in-scope improvements remain."
        )
        baseline = "› Find and fix a bug in @filename\n"
        capture = (
            "› Find and fix a bug in @filename\n\n"
            "› MainAgent: You are pro-backend-\n"
            "  runtime. Current user goal: read SPEC.md and improve AgentOrchestra\n"
            "  until no in-scope improvements remain.\n\n"
            "• Working\n"
        )
        fake = FakeTmuxSend(captures=[capture], baseline_capture=baseline)

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_does_not_accept_nonempty_capture_without_start_marker(self) -> None:
        fake = FakeTmuxSend(captures=["idle shell output\n"])

        result = send_text(
            "%8",
            "MainAgent: please review",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_reports_failure_after_retry_budget(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: still queued\n",
                "› MainAgent: still queued\n",
            ]
        )

        result = send_text("%9", "MainAgent: still queued", runner=fake, max_retries=1)

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 2)

    def test_send_text_retries_when_multiline_message_remains_in_composer(self) -> None:
        message = "MainAgent to pro-runtime-16:\nTask: Review SPEC.md\nConstraints: stay scoped"
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent to pro-runtime-16:\n  Task: Review SPEC.md\n  Constraints: stay scoped\n",
                "› MainAgent to pro-runtime-16:\n\nWorking\n",
            ]
        )

        result = send_text("%8", message, runner=fake)

        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(len(send_key_calls), 2)

    def test_fresh_capture_requirement_rejects_stale_identical_history(self) -> None:
        message = "MainAgent: please review the final change set"
        stale_capture = f"› {message}\n\n• Working\n"
        fake = FakeTmuxSend(captures=[stale_capture], baseline_capture=stale_capture)

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
            require_fresh_capture=True,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_requires_fresh_capture_by_default(self) -> None:
        message = "MainAgent: please review the final change set"
        stale_capture = f"› {message}\n\n• Working\n"
        fake = FakeTmuxSend(captures=[stale_capture], baseline_capture=stale_capture)

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_fresh_capture_requirement_accepts_new_identical_activity(self) -> None:
        message = "MainAgent: please review the final change set"
        stale_capture = f"› {message}\n\n• Working\n"
        fresh_capture = f"› {message}\n\n• Working\n› {message}\n\n• Working\n"
        fake = FakeTmuxSend(captures=[fresh_capture], baseline_capture=stale_capture)

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
            require_fresh_capture=True,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_accepts_after_fresh_probe_is_consumed_to_ready_prompt(self) -> None:
        message = "MainAgent -> pro-runtime: re-review the handoff evidence"
        fake = FakeTmuxSend(
            captures=[
                f"› {message}\n",
                "• Accept.\n\n› Find and fix a bug in @filename\n",
            ]
        )

        result = send_text(
            "%8",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_does_not_accept_ready_prompt_without_fresh_probe_seen(self) -> None:
        fake = FakeTmuxSend(captures=["• Accept.\n\n› Find and fix a bug in @filename\n"])

        result = send_text(
            "%8",
            "MainAgent -> pro-runtime: re-review the handoff evidence",
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)


if __name__ == "__main__":
    unittest.main()
