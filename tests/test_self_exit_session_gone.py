from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
from agent_orchestra_minimal.self_exit import run_self_exit  # noqa: E402


class FakeTmuxHasSessionError:
    def __init__(self) -> None:
        self.killed = False
        self.send_count = 0

    def __call__(self, args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        stdout = ""
        stderr = ""
        returncode = 0
        if args[:3] == ["tmux", "list-panes", "-a"]:
            stdout = "" if self.killed else "%9\n"
        elif args[:3] == ["tmux", "display-message", "-p"]:
            stdout = "AgentOrchestra-self-e2e-20260621-120000\n" if args[-1] == "#{session_name}" else "node\n"
        elif args[:2] == ["tmux", "capture-pane"]:
            stdout = "› /exit\n"
        elif args[:2] == ["tmux", "send-keys"] and "/exit" in args:
            self.send_count += 1
        elif args[:2] == ["tmux", "kill-pane"]:
            self.killed = True
        elif args[:2] == ["tmux", "has-session"]:
            returncode = 1
            stderr = "no server running on /tmp/tmux-501/default\n"
        return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


class SelfExitSessionGoneTests(unittest.TestCase):
    def test_tmux_has_session_error_is_not_recorded_as_session_gone(self) -> None:
        fake = FakeTmuxHasSessionError()

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
        self.assertFalse(result.session_gone)


if __name__ == "__main__":
    unittest.main()
