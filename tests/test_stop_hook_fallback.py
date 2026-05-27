from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.tmux_wake import DEFAULT_SUBMIT_KEY, run_stop_hook  # noqa: E402


class FakeTmux:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str | None]] = []
        self.capture_count = 0

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        stdout = ""
        if args[:2] == ["tmux", "capture-pane"]:
            self.capture_count += 1
            stdout = (
                "› Implement {feature}\n"
                if self.capture_count == 1
                else "› runtime_wake\n\n• Working\n"
            )
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


class StopHookFallbackTests(unittest.TestCase):
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

    def run_files(self, agent_kind: str, state: str, task_text: str) -> "_RunFiles":
        return _RunFiles(agent_kind=agent_kind, state=state, task_text=task_text)

    def tasks(self, status: str) -> str:
        return f"[status]\n{status}\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Candidates]\n\n[Done]\n"


class _RunFiles:
    def __init__(self, *, agent_kind: str, state: str, task_text: str) -> None:
        self.agent_kind = agent_kind
        self.state = state
        self.task_text = task_text
        self._tmp: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> dict[str, str]:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        task_file = root / "tasks.ini"
        state_file = root / "state.json"
        task_file.write_text(self.task_text, encoding="utf-8")
        AgentState(state=self.state, agent_id="agent", agent_kind=self.agent_kind, tmux_target="%7").write(state_file)  # type: ignore[arg-type]
        return {
            "AGENT_ORCHESTRA_TASK_FILE": str(task_file),
            "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
            "AGENT_ORCHESTRA_TMUX_PANE": "%7",
        }

    def __exit__(self, *_exc: object) -> None:
        if self._tmp is not None:
            self._tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
