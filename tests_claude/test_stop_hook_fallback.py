from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.tmux_wake import DEFAULT_SUBMIT_KEY, run_stop_hook  # noqa: E402
from stop_hook_helpers import FakeTmux, NoWakeSleepMixin, RunFiles  # noqa: E402


class StopHookFallbackTests(NoWakeSleepMixin, unittest.TestCase):
    def test_missing_tmux_environment_does_not_use_mutable_state_tmux_target(self) -> None:
        with self.run_files("MainAgent", "working", self.tasks("progress")) as env:
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNone(decision)
        self.assertEqual(fake.calls, [])

    def test_invalid_task_file_wakes_main_pane_for_quiet_professional_agent(self) -> None:
        task = "[status]\nprogress\n\n[Unexpected]\nagent added scratch notes\n"
        for missing in (True, False):
            with self.subTest(missing=missing):
                with self.run_files("ProfessionalAgent", "ready_for_review", task) as env:
                    if missing:
                        Path(env["AGENT_ORCHESTRA_TASK_FILE"]).unlink()
                    env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
                    fake = FakeTmux()
                    decision = run_stop_hook(env, runner=fake)
                self.assertIsNotNone(decision)
                self.assertTrue(decision.should_wake)
                self.assertEqual(decision.reason, "invalid_task_file_or_unreadable_main_fallback")
                self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

    def test_invalid_agent_state_wakes_main_pane_for_recovery(self) -> None:
        with self.run_files("ProfessionalAgent", "working", self.tasks("progress")) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text("{not json", encoding="utf-8")
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_agent_state_or_unreadable_main_fallback")
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

    def test_main_agent_uses_main_pane_fallback_when_state_has_no_pane_target(self) -> None:
        with self.run_files("MainAgent", "working", self.tasks("progress")) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text("{not json", encoding="utf-8")
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            env["AGENT_ORCHESTRA_AGENT_KIND"] = "MainAgent"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress")
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

    def test_invalid_professional_state_wakes_own_pane_when_kind_and_pane_are_deterministic(self) -> None:
        with self.run_files("ProfessionalAgent", "working", self.tasks("progress")) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text("{not json", encoding="utf-8")
            env["AGENT_ORCHESTRA_AGENT_KIND"] = " ProfessionalAgent "
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_agent_state_or_unreadable")
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None))

    def test_invalid_agent_state_with_invalid_kind_wakes_main_pane_for_recovery(self) -> None:
        with self.run_files("ProfessionalAgent", "working", self.tasks("progress")) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text("{not json", encoding="utf-8")
            env["AGENT_ORCHESTRA_AGENT_KIND"] = "Main Agent"
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_agent_state_or_unreadable_main_fallback")
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

    def run_files(self, agent_kind: str, state: str, task_text: str) -> RunFiles:
        return RunFiles(agent_kind=agent_kind, state=state, task_text=task_text)

    def tasks(self, status: str) -> str:
        return f"[status]\n{status}\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Candidates]\n\n[Done]\n"


if __name__ == "__main__":
    unittest.main()
