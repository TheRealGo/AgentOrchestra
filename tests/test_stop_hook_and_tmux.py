from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from agent_orchestra_minimal.tmux_wake import (  # noqa: E402
    DEFAULT_SUBMIT_KEY,
    WAKE_BUFFER_PREFIX,
    WAKE_PAYLOAD,
    run_stop_hook,
    send_wake,
)
from stop_hook_helpers import FakeTmux, RunFiles  # noqa: E402


class StopHookAndTmuxTests(unittest.TestCase):
    def test_wake_command_pastes_fixed_runtime_payload_with_named_buffer_and_submit_key(self) -> None:
        fake = FakeTmux()

        send_wake("%7", runner=fake)

        wake_buffer = self.wakeBuffer(fake)
        self.assertEqual(
            fake.calls,
            [
                (["tmux", "load-buffer", "-b", wake_buffer, "-"], WAKE_PAYLOAD),
                (["tmux", "paste-buffer", "-t", "%7", "-b", wake_buffer], None),
                (["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None),
                (["tmux", "delete-buffer", "-b", wake_buffer], None),
            ],
        )
        flattened = [part for args, _ in fake.calls for part in args]
        self.assertIn(DEFAULT_SUBMIT_KEY, flattened)
        self.assertTrue(wake_buffer.startswith(f"{WAKE_BUFFER_PREFIX}-"))

    def test_wake_command_allows_configured_submit_key(self) -> None:
        fake = FakeTmux()

        send_wake("%7", submit_key="C-m", runner=fake)

        self.assertEqual(fake.calls[-2], (["tmux", "send-keys", "-t", "%7", "C-m"], None))

    def test_main_agent_wakes_when_status_is_progress(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=self.tasks(status="progress"),
        ) as env:
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertWakeSent(fake)

    def test_main_agent_wakes_when_done_status_still_has_open_work(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=self.tasks(status="done", in_review=["review ProA result"]),
        ) as env:
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertWakeSent(fake)

    def test_main_agent_does_not_wake_when_done_and_no_open_work(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=self.tasks(status="done", done=["accepted final result"]),
        ) as env:
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertFalse(decision.should_wake)
        self.assertEqual(fake.calls, [])

    def test_professional_agent_wakes_for_unfinished_states(self) -> None:
        for state in ("working", "progress", "ready"):
            with self.subTest(state=state):
                with self.run_files(agent_kind="ProfessionalAgent", state=state) as env:
                    fake = FakeTmux()
                    decision = run_stop_hook(env, runner=fake)
                self.assertIsNotNone(decision)
                self.assertTrue(decision.should_wake)
                self.assertWakeSent(fake)

    def test_professional_agent_quiet_states_do_not_wake(self) -> None:
        for state in ("ready_for_review", "done", "needs_user", "blocked", "rate_limited", "retired"):
            with self.subTest(state=state):
                with self.run_files(agent_kind="ProfessionalAgent", state=state) as env:
                    fake = FakeTmux()
                    decision = run_stop_hook(env, runner=fake)
                self.assertIsNotNone(decision)
                self.assertFalse(decision.should_wake)
                self.assertEqual(fake.calls, [])

    def test_required_file_environment_takes_no_action_when_incomplete(self) -> None:
        with self.run_files(agent_kind="MainAgent", state="working") as complete:
            for missing_key in ("AGENT_ORCHESTRA_TASK_FILE", "AGENT_ORCHESTRA_AGENT_STATE"):
                with self.subTest(missing_key=missing_key):
                    env = dict(complete)
                    env.pop(missing_key)
                    fake = FakeTmux()
                    self.assertIsNone(run_stop_hook(env, runner=fake))
                    self.assertEqual(fake.calls, [])

    def test_missing_state_file_takes_no_action(self) -> None:
        fake = FakeTmux()
        decision = run_stop_hook(
            {
                "AGENT_ORCHESTRA_TASK_FILE": __file__,
                "AGENT_ORCHESTRA_AGENT_STATE": "/missing/state.json",
                "AGENT_ORCHESTRA_TMUX_PANE": "%7",
            },
            runner=fake,
        )

        self.assertIsNone(decision)
        self.assertEqual(fake.calls, [])

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
        self.assertEqual(fake.calls[-2], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

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

    def tasks(
        self,
        *,
        status: str,
        backlog: list[str] | None = None,
        in_progress: list[str] | None = None,
        in_review: list[str] | None = None,
        done: list[str] | None = None,
    ) -> str:
        sections = {
            "Backlog": backlog or [],
            "InProgress": in_progress or [],
            "InReview": in_review or [],
            "Done": done or [],
        }
        lines = ["[status]", status, ""]
        for section, items in sections.items():
            lines.append(f"[{section}]")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)

    def assertWakeSent(self, fake: FakeTmux) -> None:
        wake_buffer = self.wakeBuffer(fake)
        self.assertEqual(len(fake.calls), 4)
        self.assertEqual(
            fake.calls[0],
            (["tmux", "load-buffer", "-b", wake_buffer, "-"], WAKE_PAYLOAD),
        )
        self.assertEqual(fake.calls[-2], (["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None))
        self.assertEqual(fake.calls[-1], (["tmux", "delete-buffer", "-b", wake_buffer], None))

    def wakeBuffer(self, fake: FakeTmux) -> str:
        self.assertGreaterEqual(len(fake.calls), 1)
        args = fake.calls[0][0]
        self.assertEqual(args[:3], ["tmux", "load-buffer", "-b"])
        return args[3]

if __name__ == "__main__":
    unittest.main()
