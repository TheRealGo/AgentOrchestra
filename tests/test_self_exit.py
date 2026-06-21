from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
from agent_orchestra_minimal.self_exit import run_self_exit  # noqa: E402


class FakeSelfExitTmux:
    def __init__(
        self,
        *,
        closes_after_sends: int | None = None,
        capture: str = "",
        pane_command: str = "node",
        pane_command_after_exit: str | None = None,
        session_name: str = "AgentOrchestra-self-e2e-20260621-000000",
        closes_after_memory_submit: bool = False,
    ) -> None:
        self.closes_after_sends = closes_after_sends
        self.capture = capture
        self.pane_command = pane_command
        self.pane_command_after_exit = pane_command_after_exit
        self.session_name = session_name
        self.closes_after_memory_submit = closes_after_memory_submit
        self.calls: list[list[str]] = []
        self.send_count = 0
        self.memory_submit_count = 0
        self.killed = False

    def __call__(self, args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        stdout = ""
        returncode = 0
        if args[:3] == ["tmux", "list-panes", "-a"]:
            pane_exists = not self.killed and (
                self.closes_after_sends is None or self.send_count < self.closes_after_sends
            ) and not (self.closes_after_memory_submit and self.memory_submit_count > 0)
            stdout = "%9\n" if pane_exists else ""
        elif args[:3] == ["tmux", "display-message", "-p"]:
            if args[-1] == "#{session_name}":
                stdout = f"{self.session_name}\n"
            else:
                stdout = f"{(self.pane_command_after_exit if self.send_count else self.pane_command) or self.pane_command}\n"
        elif args[:2] == ["tmux", "capture-pane"]:
            stdout = self.capture
        elif args[:2] == ["tmux", "send-keys"] and "/exit" in args:
            self.send_count += 1
        elif args[:2] == ["tmux", "send-keys"] and args[-1] in {"C-m", "C-j"}:
            self.memory_submit_count += 1
        elif args[:2] == ["tmux", "kill-pane"]:
            self.killed = True
        elif args[:2] == ["tmux", "kill-session"]:
            self.killed = True
        elif args[:2] == ["tmux", "has-session"]:
            returncode = 1 if self.killed else 0
            stderr = f"can't find session: {self.session_name}\n"
            return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)
        return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr="")

class SelfExitTests(unittest.TestCase):
    def test_run_self_exit_reports_closed_after_bounded_retry(self) -> None:
        fake = FakeSelfExitTmux(closes_after_sends=2)

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=4,
            delay_seconds=0,
        )

        self.assertTrue(result.closed)
        self.assertFalse(result.killed_pane)
        self.assertEqual(result.attempts, 2)
        exit_sends = [call for call in fake.calls if call[:2] == ["tmux", "send-keys"] and "/exit" in call]
        self.assertEqual(exit_sends[0][-1], "C-m")
        self.assertEqual(exit_sends[1][-1], "C-j")

    def test_run_self_exit_accepts_native_codex_pane_command(self) -> None:
        fake = FakeSelfExitTmux(closes_after_sends=1, pane_command="codex")

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=2,
            delay_seconds=0,
        )

        self.assertTrue(result.closed)
        self.assertEqual(result.attempts, 1)

    def test_run_self_exit_clears_queued_exit_and_kills_when_pane_remains(self) -> None:
        fake = FakeSelfExitTmux(capture="› /exit\n", pane_command_after_exit="zsh")

        result = run_self_exit(
            "%9",
            submit_key="C-j",
            runner=fake,
            sleeper=lambda _: None,
            attempts=1,
            delay_seconds=0,
        )

        self.assertTrue(result.closed)
        self.assertTrue(result.cleared_leftover)
        self.assertTrue(result.killed_pane)
        self.assertEqual(result.reason, "shell_after_exit_cleanup")
        self.assertIn(["tmux", "send-keys", "-t", "%9", "Escape", "C-u"], fake.calls)
        self.assertIn(["tmux", "kill-pane", "-t", "%9"], fake.calls)

    def test_run_self_exit_does_not_force_kill_wrong_session_codex_pane_in_selfe2e_mode(self) -> None:
        fake = FakeSelfExitTmux(
            closes_after_sends=None,
            capture="› /exit\n",
            pane_command="node",
            session_name="ToO",
        )

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=1,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
        )

        self.assertFalse(result.closed)
        self.assertTrue(result.cleared_leftover)
        self.assertFalse(result.killed_pane)
        self.assertEqual(result.reason, "pane_session_mismatch_after_exit_attempt")
        self.assertEqual(result.session_name, "ToO")
        self.assertFalse(any(call[:2] == ["tmux", "kill-pane"] for call in fake.calls))
        self.assertFalse(any(call[:2] == ["tmux", "kill-session"] for call in fake.calls))

    def test_run_self_exit_allows_force_kill_dedicated_selfe2e_codex_pane_after_retries(self) -> None:
        fake = FakeSelfExitTmux(
            closes_after_sends=None,
            capture="› /exit\n",
            pane_command="node",
            session_name="AgentOrchestra-self-e2e-20260621-120000",
        )

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=1,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
        )

        self.assertTrue(result.closed)
        self.assertTrue(result.cleared_leftover)
        self.assertTrue(result.killed_pane)
        self.assertEqual(result.reason, "kill_pane_cleanup_after_exit_attempt")
        self.assertEqual(result.session_name, "AgentOrchestra-self-e2e-20260621-120000")
        self.assertTrue(result.session_gone)
        self.assertIn(["tmux", "kill-pane", "-t", "%9"], fake.calls)

    def test_run_self_exit_rejects_non_codex_shell_pane(self) -> None:
        fake = FakeSelfExitTmux(pane_command="zsh", session_name="ToO")

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=2,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
        )

        self.assertFalse(result.closed)
        self.assertEqual(result.reason, "pane_not_codex")
        self.assertEqual(result.session_name, "ToO")
        self.assertFalse(any("/exit" in call for call in fake.calls))
        self.assertFalse(any(call[:2] == ["tmux", "kill-pane"] for call in fake.calls))
        self.assertFalse(any(call[:2] == ["tmux", "kill-session"] for call in fake.calls))

    def test_run_self_exit_kills_dedicated_selfe2e_shell_pane_when_authorized(self) -> None:
        fake = FakeSelfExitTmux(
            pane_command="zsh",
            capture="zsh prompt with /exit\n",
            session_name="AgentOrchestra-self-e2e-20260621-120000",
        )

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=2,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
        )

        self.assertTrue(result.closed)
        self.assertTrue(result.killed_pane)
        self.assertTrue(result.cleared_leftover)
        self.assertEqual(result.attempts, 0)
        self.assertEqual(result.reason, "dedicated_session_shell_cleanup")
        self.assertEqual(result.session_name, "AgentOrchestra-self-e2e-20260621-120000")
        self.assertIn(["tmux", "kill-pane", "-t", "%9"], fake.calls)
        self.assertFalse(any(call[:2] == ["tmux", "kill-session"] for call in fake.calls))

    def test_run_self_exit_requires_explicit_prefix_for_selfe2e_shell_cleanup(self) -> None:
        fake = FakeSelfExitTmux(
            pane_command="zsh",
            capture="zsh prompt with /exit\n",
            session_name="AgentOrchestra-self-e2e-20260621-120000",
        )

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=2,
            delay_seconds=0,
        )

        self.assertFalse(result.closed)
        self.assertFalse(result.killed_pane)
        self.assertFalse(result.cleared_leftover)
        self.assertEqual(result.reason, "pane_not_codex")
        self.assertEqual(result.session_name, "AgentOrchestra-self-e2e-20260621-120000")
        self.assertFalse(any(call[:2] == ["tmux", "kill-pane"] for call in fake.calls))
        self.assertFalse(any(call[:2] == ["tmux", "kill-session"] for call in fake.calls))

    def test_run_self_exit_continues_memories_prompt_after_exit_attempt(self) -> None:
        fake = FakeSelfExitTmux(
            closes_after_memory_submit=True,
            capture="› [ ] Memories\n\n  Press space to select or enter to save\n",
        )
        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=2,
            delay_seconds=0,
        )

        self.assertTrue(result.closed)
        self.assertFalse(result.killed_pane)
        self.assertEqual(result.reason, "memory_prompt_closed_after_submit")
        self.assertIn(["tmux", "send-keys", "-t", "%9", "C-m"], fake.calls)
        self.assertFalse(any(call[:2] == ["tmux", "kill-pane"] for call in fake.calls))

    def test_run_self_exit_does_not_kill_cao_shell_pane_with_wrong_session(self) -> None:
        fake = FakeSelfExitTmux(pane_command="zsh", session_name="ToO")

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=2,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
        )

        self.assertFalse(result.closed)
        self.assertEqual(result.reason, "pane_not_codex")
        self.assertEqual(result.session_name, "ToO")
        self.assertFalse(any(call[:2] == ["tmux", "kill-pane"] for call in fake.calls))
        self.assertFalse(any(call[:2] == ["tmux", "kill-session"] for call in fake.calls))

    def test_run_self_exit_does_not_kill_non_shell_pane_in_selfe2e_session(self) -> None:
        fake = FakeSelfExitTmux(
            pane_command="vim",
            session_name="AgentOrchestra-self-e2e-20260621-120000",
        )

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=1,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
        )

        self.assertFalse(result.closed)
        self.assertEqual(result.reason, "pane_not_codex")
        self.assertEqual(result.session_name, "AgentOrchestra-self-e2e-20260621-120000")
        self.assertFalse(any(call[:2] == ["tmux", "kill-pane"] for call in fake.calls))
        self.assertFalse(any(call[:2] == ["tmux", "kill-session"] for call in fake.calls))
