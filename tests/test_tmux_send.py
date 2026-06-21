from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_send import _effective_cli_polls_per_attempt, send_text  # noqa: E402
from agent_orchestra_minimal.tmux_wake import DEFAULT_SUBMIT_KEY  # noqa: E402
from tmux_send_helpers import FakeTmuxSend, delivery_input_calls, submit_key_calls  # noqa: E402


class TmuxSendTests(unittest.TestCase):
    def test_installed_helper_script_can_show_help_directly(self) -> None:
        helper = ROOT / ".codex" / "agent_orchestra_minimal" / "tmux_send.py"

        result = subprocess.run(
            [sys.executable, str(helper), "--help"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("agent-orchestra-tmux-send", result.stdout)

    def test_cli_polls_per_attempt_has_busy_peer_floor(self) -> None:
        self.assertEqual(_effective_cli_polls_per_attempt(20), 60)
        self.assertEqual(_effective_cli_polls_per_attempt(60), 60)
        self.assertEqual(_effective_cli_polls_per_attempt(80), 60)

    def test_cli_polls_per_attempt_allows_short_optional_consultation(self) -> None:
        self.assertEqual(_effective_cli_polls_per_attempt(1, allow_short_polls=True), 5)
        self.assertEqual(_effective_cli_polls_per_attempt(10, allow_short_polls=True), 10)
        self.assertEqual(_effective_cli_polls_per_attempt(80, allow_short_polls=True), 60)

    def test_send_text_pastes_submits_captures_and_cleans_buffer(self) -> None:
        fake = FakeTmuxSend(captures=["› MainAgent: investigate\n\ngpt-5.5 default\nWorking\n"])

        result = send_text("%7", "MainAgent: investigate", runner=fake)

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(delivery_input_calls(fake), [(["tmux", "paste-buffer", "-t", "%7", "-b", "agent-orchestra-msg-7"], None)])
        self.assertIn((["tmux", "load-buffer", "-b", "agent-orchestra-msg-7", "-"], "MainAgent: investigate"), fake.calls)
        self.assertIn((["tmux", "delete-buffer", "-b", "agent-orchestra-msg-7"], None), fake.calls)
        self.assertIn((["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None), fake.calls)

    def test_send_text_retries_when_message_remains_in_composer(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› ProfessionalAgent: please review the contract\n",
                "› ProfessionalAgent: please review the contract\n",
                "› ProfessionalAgent: please review the contract\n\n• Working\n",
            ]
        )

        result = send_text("%8", "ProfessionalAgent: please review the contract", runner=fake)

        send_key_calls = submit_key_calls(fake)
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(len(send_key_calls), 3)

    def test_send_text_polls_before_retrying_slow_codex_tui_start(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: investigate slow startup\n",
                "› MainAgent: investigate slow startup\n\n• Working\n",
            ]
        )

        result = send_text(
            "%8",
            "MainAgent: investigate slow startup",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
        )

        send_key_calls = submit_key_calls(fake)
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(send_key_calls), 2)

    def test_send_text_can_wait_for_busy_peer_before_retrying_submit(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› MainAgent: review after current work\n",
                "› MainAgent: review after current work\n",
                "› MainAgent: review after current work\n\nExplored\n",
            ]
        )

        result = send_text(
            "%8",
            "MainAgent: review after current work",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=3,
        )

        send_key_calls = submit_key_calls(fake)
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(send_key_calls), 2)

    def test_send_text_does_not_paste_while_target_is_working(self) -> None:
        fake = FakeTmuxSend(
            captures=[],
            baseline_capture="› previous task\n\ngpt-5.5 default\n• Working\n",
        )

        result = send_text(
            "%8",
            "ProfessionalAgent: please review after you finish",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
        )

        paste_calls = delivery_input_calls(fake)
        send_key_calls = submit_key_calls(fake)
        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)
        self.assertEqual(paste_calls, [])
        self.assertEqual(send_key_calls, [])

    def test_send_text_does_not_paste_over_existing_agent_message_prompt(self) -> None:
        for baseline_capture in (
            "› MainAgent: pending review request\n",
            "› MainAgent reviewer: pending review request\n",
            "› MainAgent -> pro-runtime: pending review request\n",
            "> ProfessionalAgent: pending reply\n",
            "> ProfessionalAgent runtime-engineer: pending reply\n",
            "> ProfessionalAgent runtime-engineer -> requirements: pending reply\n",
            "› pro-runtime-16 -> pro-qa-15: pending peer consultation\n",
            "> pro-runtime-16: pending reply\n",
        ):
            with self.subTest(baseline_capture=baseline_capture):
                fake = FakeTmuxSend(captures=[], baseline_capture=baseline_capture)

                result = send_text(
                    "%8",
                    "ProfessionalAgent: please review after you finish",
                    runner=fake,
                    poll_interval_seconds=0,
                )

                paste_calls = delivery_input_calls(fake)
                send_key_calls = submit_key_calls(fake)
                self.assertFalse(result.accepted)
                self.assertEqual(result.attempts, 0)
                self.assertEqual(paste_calls, [])
                self.assertEqual(send_key_calls, [])

    def test_send_text_treats_worked_for_footer_as_completed_before_prompt(self) -> None:
        fake = FakeTmuxSend(
            captures=[
                "› ProfessionalAgent: final review please\n\n• Working\n",
            ],
            baseline_capture=(
                "› previous request\n\n"
                "• Working\n\n"
                "─ Worked for 3m 56s ────────────────────\n\n"
                "› Write tests for @filename\n"
            ),
        )

        result = send_text(
            "%8",
            "ProfessionalAgent: final review please",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
        )

        paste_calls = delivery_input_calls(fake)
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(paste_calls), 1)

    def test_send_text_does_not_treat_busy_ascii_quote_as_ready_prompt(self) -> None:
        fake = FakeTmuxSend(
            captures=[],
            baseline_capture=(
                "› previous task\n\n"
                "• Working\n"
                "> quoted shell prompt example from analysis\n"
                "  more response text\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent: review after current work",
            runner=fake,
            poll_interval_seconds=0,
        )

        paste_calls = delivery_input_calls(fake)
        send_key_calls = submit_key_calls(fake)
        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)
        self.assertEqual(paste_calls, [])
        self.assertEqual(send_key_calls, [])

    def test_send_text_does_not_treat_busy_unicode_quote_as_ready_prompt(self) -> None:
        fake = FakeTmuxSend(
            captures=[],
            baseline_capture=(
                "› previous task\n\n"
                "• Working\n"
                "› response text that starts like a prompt\n"
                "  more response text\n"
            ),
        )

        result = send_text(
            "%8",
            "MainAgent: review after current work",
            runner=fake,
            poll_interval_seconds=0,
        )

        paste_calls = delivery_input_calls(fake)
        send_key_calls = submit_key_calls(fake)
        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 0)
        self.assertEqual(paste_calls, [])
        self.assertEqual(send_key_calls, [])

    def test_send_text_waits_for_peer_to_return_to_ready_prompt_before_paste(self) -> None:
        fake = FakeTmuxSend(
            baseline_capture=[
                "› previous task\n\ngpt-5.5 default\n• Working\n",
                "• Done.\n\n› Implement {feature}\n",
                "• Done.\n\n› \n",
                "• Done.\n\n› \n",
            ],
            captures=[
                "› ProfessionalAgent: please review after you finish\n\n• Working\n",
            ],
        )

        result = send_text(
            "%8",
            "ProfessionalAgent: please review after you finish",
            runner=fake,
            poll_interval_seconds=0,
            polls_per_attempt=2,
        )

        paste_calls = delivery_input_calls(fake)
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(paste_calls), 1)

    def test_send_text_rejects_invalid_poll_bounds(self) -> None:
        cases = (
            ("max_retries", {"max_retries": -1}),
            ("max_retries", {"max_retries": 11}),
            ("polls_per_attempt", {"polls_per_attempt": 0}),
            ("polls_per_attempt", {"polls_per_attempt": 61}),
            ("poll_interval_seconds", {"poll_interval_seconds": -0.1}),
            ("poll_interval_seconds", {"poll_interval_seconds": 2.1}),
        )
        for pattern, kwargs in cases:
            with self.subTest(pattern=pattern), self.assertRaisesRegex(ValueError, pattern):
                send_text("%8", "MainAgent: investigate", runner=FakeTmuxSend(captures=[]), **kwargs)

    def test_send_text_rejects_non_deterministic_tmux_targets(self) -> None:
        for pane_target in ("1", ":0.1", "%7 other", "%7\nsend", ""):
            with self.subTest(pane_target=pane_target), self.assertRaisesRegex(ValueError, "pane"):
                send_text(pane_target, "MainAgent: investigate", runner=FakeTmuxSend(captures=[]))

    def test_send_text_defaults_blank_submit_key(self) -> None:
        fake = FakeTmuxSend(captures=["› MainAgent: investigate\n\nWorking\n"])

        result = send_text("%7", "MainAgent: investigate", submit_key="  ", runner=fake)

        self.assertTrue(result.accepted)
        self.assertIn((["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None), fake.calls)
