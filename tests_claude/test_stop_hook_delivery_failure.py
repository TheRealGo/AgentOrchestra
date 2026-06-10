from __future__ import annotations

import io
import subprocess
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.tmux_wake import run_stop_hook  # noqa: E402
from stop_hook_helpers import FakeTmux, NoWakeSleepMixin, RunFiles  # noqa: E402


PROGRESS_TASK = (
    "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n"
    "[InReview]\n\n[Candidates]\n\n[Done]\n"
)


class StuckComposerTmux(FakeTmux):
    """A capture would show the payload still in the composer.

    For Codex this signalled an unaccepted delivery. The Claude wake never
    captures, so this runner behaves identically to a plain fake: the captured
    state is irrelevant to a fire-and-forget wake.
    """

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        stdout = "❯ runtime_wake source=hook user_instruction=false\n" if args[:2] == ["tmux", "capture-pane"] else ""
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


class FailingSendKeysTmux(FakeTmux):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        if args[:2] == ["tmux", "send-keys"]:
            raise subprocess.CalledProcessError(returncode=1, cmd=args, stderr="pane not found")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")


class StopHookDeliveryFailureTests(NoWakeSleepMixin, unittest.TestCase):
    def test_wake_is_fire_and_forget_and_does_not_poll_confirm(self) -> None:
        # Claude's wake cannot poll-confirm (it would deadlock on the agent's own
        # Stop Hook). It pastes and presses submit three times, never captures the
        # pane, and reports the plain decision reason with no delivery suffix.
        with RunFiles(agent_kind="MainAgent", state="working", task_text=PROGRESS_TASK) as env:
            fake = StuckComposerTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress")
        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertEqual(len(send_key_calls), 3)
        self.assertFalse(any(call[0][:2] == ["tmux", "capture-pane"] for call in fake.calls))

    def test_invalid_agent_state_fallback_reports_plain_main_fallback_reason(self) -> None:
        with RunFiles(agent_kind="ProfessionalAgent", state="working", task_text=PROGRESS_TASK) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text("{not json", encoding="utf-8")
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = StuckComposerTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_agent_state_or_unreadable_main_fallback")

    def test_stop_hook_reports_wake_delivery_failure_when_tmux_send_fails(self) -> None:
        with RunFiles(agent_kind="MainAgent", state="working", task_text=PROGRESS_TASK) as env:
            fake = FailingSendKeysTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress_wake_delivery_failed")

    def test_stop_hook_entrypoint_surfaces_wake_delivery_issue(self) -> None:
        import importlib.util

        hook_path = ROOT / ".claude" / "hooks" / "agent_orchestra_stop_hook.py"
        spec = importlib.util.spec_from_file_location("agent_orchestra_stop_hook_claude", hook_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stderr = StringIO()

        decision = type("Decision", (), {"reason": "main_status_progress_wake_delivery_failed"})()
        with patch.object(module, "run_stop_hook", return_value=decision):
            # The Claude Code hook reads/drains JSON stdin before deciding.
            with patch.object(module.sys, "stdin", io.StringIO('{"hook_event_name":"Stop"}')):
                with redirect_stderr(stderr):
                    exit_code = module.main()

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "agent-orchestra Stop Hook wake issue: main_status_progress_wake_delivery_failed",
            stderr.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
