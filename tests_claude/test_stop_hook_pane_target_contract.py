from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.tmux_wake import DEFAULT_SUBMIT_KEY, run_stop_hook  # noqa: E402
from stop_hook_helpers import FakeTmux, NoWakeSleepMixin, RunFiles, task_text  # noqa: E402


class StopHookPaneTargetContractTests(NoWakeSleepMixin, unittest.TestCase):
    def test_launch_environment_pane_takes_precedence_over_mutable_state_target(self) -> None:
        with RunFiles(agent_kind="MainAgent", state="working", task_text=task_text(status="progress")) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text(
                '{"agent_id":"main","agent_kind":"MainAgent","state":"working","tmux_target":"%state"}\n',
                encoding="utf-8",
            )
            env["AGENT_ORCHESTRA_TMUX_PANE"] = "%env"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%env", DEFAULT_SUBMIT_KEY], None))

    def test_invalid_launch_environment_pane_uses_main_fallback_instead_of_mutable_state_target(self) -> None:
        with RunFiles(agent_kind="MainAgent", state="working", task_text=task_text(status="progress")) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text(
                '{"agent_id":"main","agent_kind":"MainAgent","state":"working","tmux_target":"%state"}\n',
                encoding="utf-8",
            )
            env["AGENT_ORCHESTRA_TMUX_PANE"] = ":0.1"
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

    def test_missing_launch_environment_pane_takes_no_action_instead_of_using_mutable_state_target(self) -> None:
        with RunFiles(agent_kind="MainAgent", state="working", task_text=task_text(status="progress")) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text(
                '{"agent_id":"main","agent_kind":"MainAgent","state":"working","tmux_target":"%state"}\n',
                encoding="utf-8",
            )
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNone(decision)
        self.assertEqual(fake.calls, [])

    def test_stop_hook_does_not_use_shell_tmux_pane_as_authoritative_target(self) -> None:
        with RunFiles(agent_kind="ProfessionalAgent", state="working", task_text=task_text(status="done")) as env:
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            env["TMUX_PANE"] = "%shell"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNone(decision)
        self.assertEqual(fake.calls, [])

    def test_missing_launch_environment_pane_does_not_fallback_to_tmux_pane(self) -> None:
        with RunFiles(agent_kind="MainAgent", state="working", task_text=task_text(status="progress")) as env:
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            env["TMUX_PANE"] = "%inherited"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNone(decision)
        self.assertEqual(fake.calls, [])

    def test_missing_launch_environment_pane_prefers_main_fallback_over_tmux_pane(self) -> None:
        with RunFiles(agent_kind="ProfessionalAgent", state="working", task_text=task_text(status="progress")) as env:
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            env["TMUX_PANE"] = "%inherited"
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "professional_active_working_main_fallback")
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY], None))

    def test_invalid_mutable_state_pane_metadata_does_not_rekick_quiet_professional_agent(self) -> None:
        with RunFiles(
            agent_kind="ProfessionalAgent",
            state="ready_for_review",
            task_text=task_text(status="done"),
        ) as env:
            Path(env["AGENT_ORCHESTRA_AGENT_STATE"]).write_text(
                '{"agent_id":"pro","agent_kind":"ProfessionalAgent","state":"ready_for_review","tmux_target":":0.1"}\n',
                encoding="utf-8",
            )
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertFalse(decision.should_wake)
        self.assertEqual(decision.reason, "professional_quiet_ready_for_review")
        self.assertEqual(fake.calls, [])


if __name__ == "__main__":
    unittest.main()
