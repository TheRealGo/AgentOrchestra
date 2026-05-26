from __future__ import annotations

import subprocess
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.tmux_wake import run_stop_hook  # noqa: E402
from stop_hook_helpers import FakeTmux, RunFiles  # noqa: E402


class ComposerStuckTmux(FakeTmux):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        stdout = ""
        if args[:2] == ["tmux", "capture-pane"]:
            stdout = "› runtime_wake source=hook user_instruction=false\n"
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


class FailingSendKeysTmux(FakeTmux):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        if args[:2] == ["tmux", "send-keys"]:
            raise subprocess.CalledProcessError(returncode=1, cmd=args, stderr="pane not found")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")


class StopHookDeliveryFailureTests(unittest.TestCase):
    def test_stop_hook_reports_wake_delivery_failure_when_payload_remains_in_composer(self) -> None:
        with RunFiles(
            agent_kind="MainAgent",
            state="working",
            task_text=(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n"
                "[InReview]\n\n[Candidates]\n\n[Done]\n"
            ),
        ) as env:
            fake = ComposerStuckTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress_wake_delivery_unaccepted")
        send_key_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "send-keys"]]
        self.assertEqual(len(send_key_calls), 3)

    def test_invalid_agent_state_fallback_reports_wake_delivery_failure(self) -> None:
        with RunFiles(
            agent_kind="ProfessionalAgent",
            state="working",
            task_text=(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n"
                "[InReview]\n\n[Candidates]\n\n[Done]\n"
            ),
        ) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text("{not json", encoding="utf-8")
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = ComposerStuckTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(
            decision.reason,
            "invalid_agent_state_or_unreadable_main_fallback_wake_delivery_unaccepted",
        )

    def test_stop_hook_reports_wake_delivery_failure_when_tmux_send_fails(self) -> None:
        with RunFiles(
            agent_kind="MainAgent",
            state="working",
            task_text=(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n"
                "[InReview]\n\n[Candidates]\n\n[Done]\n"
            ),
        ) as env:
            fake = FailingSendKeysTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress_wake_delivery_failed")

    def test_stop_hook_entrypoint_surfaces_wake_delivery_issue(self) -> None:
        import importlib.util

        hook_path = ROOT / ".codex" / "hooks" / "agent_orchestra_stop_hook.py"
        spec = importlib.util.spec_from_file_location("agent_orchestra_stop_hook", hook_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stderr = StringIO()

        decision = type("Decision", (), {"reason": "main_status_progress_wake_delivery_failed"})()
        with patch.object(module, "run_stop_hook", return_value=decision):
            with redirect_stderr(stderr):
                exit_code = module.main()

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "agent-orchestra Stop Hook wake issue: main_status_progress_wake_delivery_failed",
            stderr.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
