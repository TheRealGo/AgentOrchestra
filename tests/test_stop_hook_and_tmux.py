from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from agent_orchestra_minimal.tmux_wake import (  # noqa: E402
    DEFAULT_SUBMIT_KEY,
    WAKE_BUFFER_PREFIX,
    WAKE_PAYLOAD,
    run_stop_hook,
    send_wake,
)
from stop_hook_helpers import FakeTmux, RunFiles, task_text  # noqa: E402


class StopHookAndTmuxTests(unittest.TestCase):
    def test_wake_command_pastes_fixed_runtime_payload_with_named_buffer_and_submit_key(self) -> None:
        fake = FakeTmux()

        result = send_wake("%7", runner=fake)

        self.assertTrue(result.accepted)
        load_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "load-buffer"]]
        self.assertEqual(len(load_calls), 1)
        self.assertIn("runtime_wake", load_calls[0][1] or "")
        self.assertIn("user_instruction=false", load_calls[0][1] or "")
        self.assertIn("resync=startup_agents_role_contract_team_skill_task_state", load_calls[0][1] or "")
        self.assertIn("action=resume_existing_work_after_resync", load_calls[0][1] or "")
        self.assertIn((["tmux", "paste-buffer", "-t", "%7", "-b", "agent-orchestra-wake-7"], None), fake.calls)
        flattened = [part for args, _ in fake.calls for part in args]
        self.assertIn(DEFAULT_SUBMIT_KEY, flattened)

    def test_wake_command_allows_configured_submit_key(self) -> None:
        fake = FakeTmux()

        send_wake("%7", submit_key="C-m", runner=fake)

        self.assertIn((["tmux", "send-keys", "-t", "%7", "C-m"], None), fake.calls)

    def test_wake_command_defaults_blank_submit_key(self) -> None:
        fake = FakeTmux()

        send_wake("%7", submit_key="  ", runner=fake)

        self.assertIn((["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None), fake.calls)

    def test_wake_command_does_not_accept_stale_identical_payload(self) -> None:
        fake = FakeTmux()
        fake.capture_count = 10

        result = send_wake(
            "%7",
            runner=fake,
        )

        self.assertFalse(result.accepted)

    def test_main_agent_wakes_when_status_is_progress(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=task_text(status="progress"),
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
            task_text=task_text(status="done", in_review=["review ProA result"]),
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
            task_text=task_text(status="done", done=["accepted final result"]),
        ) as env:
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertFalse(decision.should_wake)
        self.assertEqual(fake.calls, [])

    def test_main_agent_wakes_when_done_but_selfe2e_status_is_still_progress(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=task_text(status="done", done=["accepted final result"]),
        ) as env:
            root = Path(env["AGENT_ORCHESTRA_TASK_FILE"]).parent
            status_file = root / ".tmp" / "self-improvement-e2e" / "status"
            status_file.parent.mkdir(parents=True)
            status_file.write_text("progress", encoding="utf-8")
            env["AGENT_ORCHESTRA_EDIT_ROOT"] = str(root)
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_done_with_selfe2e_status_not_done")
        self.assertWakeSent(fake)

    def test_main_agent_wakes_when_done_but_sibling_professional_agent_is_not_retired(self) -> None:
        for state in ("ready", "working", "ready_for_review", "done", "blocked"):
            with self.subTest(state=state):
                with self.run_files(
                    agent_kind="MainAgent",
                    state="working",
                    task_text=task_text(status="done", done=["accepted final result"]),
                ) as env:
                    self.write_sibling_professional_state(env, state)
                    fake = FakeTmux()
                    decision = run_stop_hook(env, runner=fake)

                self.assertIsNotNone(decision)
                self.assertTrue(decision.should_wake)
                self.assertEqual(decision.reason, "main_done_with_unretired_professional_agents")
                self.assertWakeSent(fake)

    def test_main_agent_stays_quiet_when_done_and_sibling_professional_agent_is_retired(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=task_text(status="done", done=["accepted final result"]),
        ) as env:
            self.write_sibling_professional_state(env, "retired")
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertFalse(decision.should_wake)
        self.assertEqual(fake.calls, [])

    def test_main_agent_wakes_when_done_but_sibling_professional_agent_state_is_invalid(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=task_text(status="done", done=["accepted final result"]),
        ) as env:
            agent_dir = Path(env["AGENT_ORCHESTRA_TASK_FILE"]).parent / "agents" / "pa-invalid"
            agent_dir.mkdir(parents=True)
            (agent_dir / "state.json").write_text("not-a-valid-state\n", encoding="utf-8")
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_done_with_unretired_professional_agents")
        self.assertWakeSent(fake)

    def test_main_agent_wakes_when_done_status_has_unresolved_candidate(self) -> None:
        with self.run_files(
            agent_kind="MainAgent",
            state="working",
            task_text=task_text(
                status="done",
                candidates=["candidate-1: disposition=open; summary=send retry helper"],
                done=["accepted current patch"],
            ),
        ) as env:
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_done_with_unresolved_candidates")
        self.assertWakeSent(fake)

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

    def run_files(
        self,
        *,
        agent_kind: str,
        state: str,
        task_text: str | None = None,
    ) -> RunFiles:
        return RunFiles(agent_kind=agent_kind, state=state, task_text=task_text or DEFAULT_TASK_FILE)

    def assertWakeSent(self, fake: FakeTmux) -> None:
        load_calls = [call for call in fake.calls if call[0][:2] == ["tmux", "load-buffer"]]
        self.assertEqual(len(load_calls), 1)
        self.assertIn("runtime_wake", load_calls[0][1] or "")
        self.assertIn((["tmux", "paste-buffer", "-t", "%7", "-b", "agent-orchestra-wake-7"], None), fake.calls)
        self.assertIn((["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None), fake.calls)
        self.assertIn((["tmux", "delete-buffer", "-b", "agent-orchestra-wake-7"], None), fake.calls)

    def write_sibling_professional_state(self, env: dict[str, str], state: str) -> None:
        agent_dir = Path(env["AGENT_ORCHESTRA_TASK_FILE"]).parent / "agents" / "pa-sibling"
        AgentState(
            state=state,  # type: ignore[arg-type]
            agent_id="pa-sibling",
            agent_kind="ProfessionalAgent",
            tmux_target="%9",
        ).write(agent_dir / "state.json")

    def wakeBuffer(self, fake: FakeTmux) -> str:
        self.assertGreaterEqual(len(fake.calls), 1)
        args = fake.calls[0][0]
        self.assertEqual(args[:3], ["tmux", "load-buffer", "-b"])
        return args[3]

if __name__ == "__main__":
    unittest.main()
