from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from agent_orchestra_minimal.tmux_wake import DEFAULT_SUBMIT_KEY, WAKE_PAYLOAD, run_stop_hook  # noqa: E402
from stop_hook_helpers import FakeTmux, RunFiles  # noqa: E402


class StopHookInvalidTaskFileTests(unittest.TestCase):
    def test_missing_task_file_wakes_main_agent_for_repair(self) -> None:
        with self.run_files(agent_kind="MainAgent", state="working") as env:
            Path(env["AGENT_ORCHESTRA_TASK_FILE"]).unlink()
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_task_file_or_unreadable")
        self.assertWakeSent(fake)

    def test_missing_task_file_wakes_active_professional_agent_for_repair(self) -> None:
        with self.run_files(agent_kind="ProfessionalAgent", state="working") as env:
            Path(env["AGENT_ORCHESTRA_TASK_FILE"]).unlink()
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_task_file_or_unreadable")
        self.assertWakeSent(fake)

    def test_missing_task_file_stays_quiet_without_main_fallback_for_quiet_professional_agent(self) -> None:
        with self.run_files(agent_kind="ProfessionalAgent", state="ready_for_review") as env:
            Path(env["AGENT_ORCHESTRA_TASK_FILE"]).unlink()
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertFalse(decision.should_wake)
        self.assertEqual(fake.calls, [])

    def test_retired_professional_agent_with_missing_task_file_wakes_main_for_repair(self) -> None:
        with self.run_files(agent_kind="ProfessionalAgent", state="retired") as env:
            Path(env["AGENT_ORCHESTRA_TASK_FILE"]).unlink()
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            env.pop("TMUX_PANE", None)
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_task_file_or_unreadable_main_fallback")
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

    def test_invalid_task_file_wakes_main_agent_for_repair(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text="[status]\nprogress\n\n[Unexpected]\nagent added scratch notes\n",
        ) as env:
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_task_file_or_unreadable")
        self.assertWakeSent(fake)

    def test_invalid_task_file_wakes_active_professional_agent_for_repair(self) -> None:
        with self.run_files(
            agent_kind="ProfessionalAgent",
            state="working",
            task_text="[status]\nprogress\n\n[Unexpected]\nagent added scratch notes\n",
        ) as env:
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_task_file_or_unreadable")
        self.assertWakeSent(fake)

    def run_files(
        self,
        *,
        agent_kind: str,
        state: str,
        task_text: str | None = None,
    ) -> RunFiles:
        return RunFiles(agent_kind=agent_kind, state=state, task_text=task_text or DEFAULT_TASK_FILE)

    def assertWakeSent(self, fake: FakeTmux) -> None:
        wake_buffer = self.wakeBuffer(fake)
        self.assertEqual(len(fake.calls), 6)
        self.assertEqual(
            fake.calls[0],
            (["tmux", "load-buffer", "-b", wake_buffer, "-"], WAKE_PAYLOAD),
        )
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None))
        self.assertEqual(fake.calls[-1], (["tmux", "delete-buffer", "-b", wake_buffer], None))

    def wakeBuffer(self, fake: FakeTmux) -> str:
        self.assertGreaterEqual(len(fake.calls), 1)
        args = fake.calls[0][0]
        self.assertEqual(args[:3], ["tmux", "load-buffer", "-b"])
        return args[3]


if __name__ == "__main__":
    unittest.main()
