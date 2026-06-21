from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxStartupRecoveryTests(unittest.TestCase):
    def test_send_text_recovers_from_update_notice_before_pasting(self) -> None:
        message = "MainAgent -> pro-runtime: accept scoped task"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture=[
                "✨ Update available! 0.137.0 -> 0.138.0\n",
                "› Find and fix a bug in @filename\n",
            ],
        )

        result = send_text(
            "%8",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
            max_retries=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertIn(["tmux", "send-keys", "-t", "%8", "C-m"], self._send_key_calls(fake))

    def test_send_text_recovers_from_mcp_startup_warning_before_pasting(self) -> None:
        message = "MainAgent -> pro-backend: accept scoped task"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture=[
                "MCP client failed to start: colab-mcp exited during handshake\n",
                "MCP client failed to start: colab-mcp exited during handshake\n",
                "› Find and fix a bug in @filename\n",
            ],
        )

        result = send_text(
            "%9",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=3,
            max_retries=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertIn(["tmux", "send-keys", "-t", "%9", "C-m"], self._send_key_calls(fake))
        self.assertIn(["tmux", "send-keys", "-t", "%9", "Escape"], self._send_key_calls(fake))

    def test_send_text_recovers_from_weekly_limit_notice_before_pasting(self) -> None:
        message = "MainAgent -> pro-ui: accept scoped task"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture=[
                "⚠ Heads up, you have less than 10% of your weekly limit left.\n",
                "⚠ Heads up, you have less than 10% of your weekly limit left.\n",
                "› Implement {feature}\n",
                "› \n",
            ],
        )

        result = send_text(
            "%12",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=4,
            max_retries=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertIn(["tmux", "send-keys", "-t", "%12", "C-m"], self._send_key_calls(fake))
        self.assertIn(["tmux", "send-keys", "-t", "%12", "Escape"], self._send_key_calls(fake))
        self.assertIn(["tmux", "send-keys", "-t", "%12", "Escape", "C-u"], self._send_key_calls(fake))

    def test_send_text_escapes_model_choice_menu_before_pasting(self) -> None:
        message = "MainAgent -> pro-requirements: accept scoped task"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture=[
                "› 1. Switch to gpt-5.1\n  2. Keep current model\n  Press enter to confirm or esc to dismiss\n",
                "› Implement {feature}\n",
                "› \n",
            ],
        )

        result = send_text(
            "%13",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=3,
            max_retries=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertIn(["tmux", "send-keys", "-t", "%13", "Escape"], self._send_key_calls(fake))
        self.assertIn(["tmux", "send-keys", "-t", "%13", "Escape", "C-u"], self._send_key_calls(fake))

    def test_send_text_can_recover_from_something_went_wrong_screen(self) -> None:
        message = "MainAgent -> pro-runtime: summarize after TUI error"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture="■ Something went wrong?\n  tell the model what to do differently\n",
        )

        result = send_text(
            "%15",
            message,
            runner=fake,
            allow_interrupted_recovery=True,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_send_text_clears_default_composer_before_pasting(self) -> None:
        message = "MainAgent -> pro-docs: accept scoped task"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture=[
                "› Implement {feature}\n",
                "› \n",
            ],
        )

        result = send_text(
            "%14",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
            max_retries=0,
        )

        self.assertTrue(result.accepted)
        self.assertIn(["tmux", "send-keys", "-t", "%14", "Escape", "C-u"], self._send_key_calls(fake))

    def test_send_text_clears_write_tests_default_composer_before_pasting(self) -> None:
        message = "MainAgent -> pro-qa: accept scoped task"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture=[
                "› Write tests for @filename\n",
                "› \n",
            ],
        )

        result = send_text(
            "%14",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
            max_retries=0,
        )

        self.assertTrue(result.accepted)
        self.assertIn(["tmux", "send-keys", "-t", "%14", "Escape", "C-u"], self._send_key_calls(fake))

    def test_send_text_waits_for_mcp_startup_progress_before_pasting(self) -> None:
        message = "MainAgent -> pro-runtime: accept scoped task"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture=[
                "• Starting MCP servers (6/7): playwright (19s • esc to interrupt)\n\n› Implement {feature}\n",
                "• Starting MCP servers (6/7): playwright (20s • esc to interrupt)\n\n› Implement {feature}\n",
                "› Implement {feature}\n",
                "› \n",
            ],
        )

        result = send_text(
            "%14",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=4,
            max_retries=0,
        )

        self.assertTrue(result.accepted)
        paste_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "paste-buffer"] or "-l" in call[0]]
        self.assertEqual(len(paste_calls), 1)
        self.assertIn(["tmux", "send-keys", "-t", "%14", "Escape", "C-u"], self._send_key_calls(fake))

    def test_send_text_does_not_accept_mcp_startup_as_agent_work(self) -> None:
        message = "MainAgent: start AgenticRAG E2E"
        fake = FakeTmuxSend(
            captures=[
                f"› {message}\n\n• No previous message to edit.\n\n› complete.\n",
                f"› {message}\n\n• Starting MCP servers (6/7): colab-mcp\n\n› Implement {{feature}}\n",
            ],
            baseline_capture=["› Implement {feature}\n", "› \n"],
        )

        result = send_text(
            "%15",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=1,
            max_retries=1,
        )

        self.assertFalse(result.accepted)

    def test_send_text_uses_tail_probe_and_alternate_submit_for_long_assignment(self) -> None:
        message = (
            "MainAgent: You are runtime-agent. Review AgenticRAG autonomous runtime.\n"
            "Requirements: reject deterministic fallback and function-calling-only behavior.\n"
            "output: implement needed changes in repo, run focused unittest/py_compile "
            "checks you own, report requirement ids covered, files changed, evidence "
            "paths/commands, remaining risks, and blocking_objection if any."
        )
        queued_tail = (
            "› output: implement needed changes in repo, run focused\n"
            "  unittest/py_compile checks you own, report requirement ids covered,\n"
            "  files changed, evidence paths/commands, remaining risks, and\n"
            "  blocking_objection if any.\n"
        )
        fake = FakeTmuxSend(
            captures=[
                queued_tail,
                queued_tail,
                "• Working\n",
            ],
            baseline_capture="› Improve documentation in @filename\n",
        )

        result = send_text(
            "%10",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=1,
            max_retries=1,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertIn(["tmux", "send-keys", "-t", "%10", "C-m"], self._send_key_calls(fake))
        self.assertIn(["tmux", "send-keys", "-t", "%10", "C-j"], self._send_key_calls(fake))

    def test_send_text_uses_normalized_tail_probe_for_assignment_tail(self) -> None:
        message = (
            "MainAgent: You are pro-ui. Review AgenticRAG visual interaction.\n"
            "Inspect the map, object circles, breathing active state, magician hat "
            "transformation, desktop and mobile evidence, and all UI issues you observe.\n"
            "Do not mark the whole run complete."
        )
        tail = " ".join(message.split())[-56:]
        fake = FakeTmuxSend(
            captures=[
                f"› {tail}\n",
                f"› {tail}\n",
                "• Working\n",
            ],
            baseline_capture="› Implement {feature}\n",
        )

        result = send_text(
            "%11",
            message,
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=1,
            max_retries=1,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertIn(["tmux", "send-keys", "-t", "%11", "C-j"], self._send_key_calls(fake))

    def _send_key_calls(self, fake: FakeTmuxSend) -> list[list[str]]:
        return [call[0] for call in fake.calls if call[0][:2] == ["tmux", "send-keys"] and "-l" not in call[0]]


if __name__ == "__main__":
    unittest.main()
