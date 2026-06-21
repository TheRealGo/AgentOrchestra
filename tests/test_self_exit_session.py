from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
from agent_orchestra_minimal.self_exit import main, run_self_exit  # noqa: E402
from agent_orchestra_minimal.self_exit_session import cleanup_auxiliary_shell_panes  # noqa: E402


class FakeSessionTmux:
    def __init__(
        self,
        session_name: str = "AgentOrchestra-self-e2e-20260621-120000",
        has_session_stderr: str | None = None,
    ) -> None:
        self.session_name = session_name
        self.has_session_stderr = has_session_stderr or f"can't find session: {session_name}\n"
        self.killed: set[str] = set()
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        stdout = ""
        if args[:3] == ["tmux", "list-panes", "-a"]:
            stdout = "" if "%9" in self.killed else "%9\n"
        elif args[:3] == ["tmux", "list-panes", "-t"]:
            stdout = "%8\tbash\n%9\tnode\n%10\tzsh\n%11\tvim\n"
        elif args[:3] == ["tmux", "display-message", "-p"]:
            stdout = f"{self.session_name}\n" if args[-1] == "#{session_name}" else "node\n"
        elif args[:2] == ["tmux", "kill-pane"]:
            self.killed.add(args[-1])
        elif args[:2] == ["tmux", "has-session"]:
            returncode = 1 if "%9" in self.killed else 0
            return subprocess.CompletedProcess(
                args=args,
                returncode=returncode,
                stdout=stdout,
                stderr=self.has_session_stderr,
            )
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


class SelfExitSessionTests(unittest.TestCase):
    def test_cleanup_auxiliary_shell_panes_is_prefix_scoped_and_skips_main_pane(self) -> None:
        fake = FakeSessionTmux()

        killed = cleanup_auxiliary_shell_panes(
            fake,
            session_name="AgentOrchestra-self-e2e-20260621-120000",
            session_prefix="AgentOrchestra-self-e2e-",
            exclude_pane="%9",
        )

        self.assertEqual(killed, ("%8", "%10"))
        self.assertEqual(fake.killed, {"%8", "%10"})
        self.assertFalse(any(call[-1] == "%11" for call in fake.calls if call[:2] == ["tmux", "kill-pane"]))

    def test_cleanup_auxiliary_shell_panes_rejects_wrong_session_prefix(self) -> None:
        fake = FakeSessionTmux(session_name="ToO")

        killed = cleanup_auxiliary_shell_panes(
            fake,
            session_name="ToO",
            session_prefix="AgentOrchestra-self-e2e-",
            exclude_pane="%9",
        )

        self.assertEqual(killed, ())
        self.assertEqual(fake.calls, [])

    def test_run_self_exit_records_auxiliary_shell_cleanup_when_enabled(self) -> None:
        fake = FakeSessionTmux()

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=1,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
            cleanup_auxiliary_shells=True,
        )

        self.assertTrue(result.closed)
        self.assertEqual(result.auxiliary_shell_panes, ("%8", "%10"))
        self.assertTrue(result.session_gone)
        self.assertEqual(fake.killed, {"%8", "%9", "%10"})

    def test_run_self_exit_does_not_record_session_gone_for_tmux_runtime_error(self) -> None:
        fake = FakeSessionTmux(has_session_stderr="no server running on /tmp/tmux-501/default\n")

        result = run_self_exit(
            "%9",
            submit_key="C-m",
            runner=fake,
            sleeper=lambda _: None,
            attempts=1,
            delay_seconds=0,
            allow_shell_cleanup_session_prefix="AgentOrchestra-self-e2e-",
            cleanup_auxiliary_shells=True,
        )

        self.assertTrue(result.closed)
        self.assertFalse(result.session_gone)

    def test_cli_requires_explicit_shell_cleanup_prefix(self) -> None:
        parser_actions = []
        original = run_self_exit
        try:

            def fake_run_self_exit(*_: object, **kwargs: object) -> object:
                parser_actions.append(kwargs)
                raise SystemExit(0)

            import agent_orchestra_minimal.self_exit as self_exit

            self_exit.run_self_exit = fake_run_self_exit  # type: ignore[assignment]
            with self.assertRaises(SystemExit):
                main(["--pane", "%9", "--foreground"])
        finally:
            import agent_orchestra_minimal.self_exit as self_exit

            self_exit.run_self_exit = original  # type: ignore[assignment]

        self.assertIsNone(parser_actions[0]["allow_shell_cleanup_session_prefix"])
        self.assertFalse(parser_actions[0]["cleanup_auxiliary_shells"])


if __name__ == "__main__":
    unittest.main()
