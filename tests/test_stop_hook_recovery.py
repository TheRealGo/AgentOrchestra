from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from agent_orchestra_minimal.tmux_wake import run_stop_hook  # noqa: E402


class FakeTmux:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str | None]] = []

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")


class StopHookRecoveryTests(unittest.TestCase):
    def test_missing_main_state_wakes_when_task_file_has_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text("[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Done]\n", encoding="utf-8")
            fake = FakeTmux()
            decision = run_stop_hook(self.env(task_file, Path(tmpdir) / "missing.json", "MainAgent"), runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress")
        self.assertTrue(any(call[0][:3] == ["tmux", "send-keys", "-t"] for call in fake.calls))

    def test_missing_main_state_stays_quiet_when_task_file_is_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            fake = FakeTmux()
            decision = run_stop_hook(self.env(task_file, Path(tmpdir) / "missing.json", "MainAgent"), runner=fake)

        self.assertIsNotNone(decision)
        self.assertFalse(decision.should_wake)
        self.assertEqual(fake.calls, [])

    def test_missing_professional_state_takes_no_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            fake = FakeTmux()
            decision = run_stop_hook(
                self.env(task_file, Path(tmpdir) / "missing.json", "ProfessionalAgent"),
                runner=fake,
            )

        self.assertIsNone(decision)
        self.assertEqual(fake.calls, [])

    def env(self, task_file: Path, state_file: Path, agent_kind: str) -> dict[str, str]:
        return {
            "AGENT_ORCHESTRA_TASK_FILE": str(task_file),
            "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
            "AGENT_ORCHESTRA_AGENT_KIND": agent_kind,
            "AGENT_ORCHESTRA_TMUX_PANE": "%7",
        }


if __name__ == "__main__":
    unittest.main()
