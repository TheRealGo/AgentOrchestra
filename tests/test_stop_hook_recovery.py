from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from agent_orchestra_minimal.tmux_wake import DEFAULT_SUBMIT_KEY, WAKE_PAYLOAD, run_stop_hook  # noqa: E402


WAKE_PROMPT = " ".join(WAKE_PAYLOAD.split())


class FakeTmux:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str | None]] = []
        self.capture_count = 0
        self.composer_cleared = False
        self.paste_seen = False

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        stdout = ""
        if args[:2] == ["tmux", "send-keys"] and args[-2:] == ["Escape", "C-u"]:
            self.composer_cleared = True
        if args[:2] == ["tmux", "paste-buffer"]:
            self.paste_seen = True
        if len(args) >= 6 and args[:3] == ["tmux", "send-keys", "-t"] and "-l" in args:
            self.paste_seen = True
        if args[:2] == ["tmux", "capture-pane"]:
            self.capture_count += 1
            if self.capture_count == 1:
                stdout = "› Implement {feature}\n"
            elif self.composer_cleared and not self.paste_seen:
                stdout = "› \n"
            else:
                stdout = f"› {WAKE_PROMPT}\n\n• Working\n"
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


class BusyThenReadyTmux(FakeTmux):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        stdout = ""
        if args[:2] == ["tmux", "send-keys"] and args[-2:] == ["Escape", "C-u"]:
            self.composer_cleared = True
        if args[:2] == ["tmux", "paste-buffer"]:
            self.paste_seen = True
        if len(args) >= 6 and args[:3] == ["tmux", "send-keys", "-t"] and "-l" in args:
            self.paste_seen = True
        if args[:2] == ["tmux", "capture-pane"]:
            self.capture_count += 1
            if self.capture_count < 7:
                stdout = "• Working\n"
            elif self.capture_count == 7:
                stdout = "› Implement {feature}\n"
            elif self.composer_cleared and not self.paste_seen:
                stdout = "› \n"
            else:
                stdout = f"› {WAKE_PROMPT}\n\n• Working\n"
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


class StopHookRecoveryTests(unittest.TestCase):
    def test_missing_main_state_wakes_when_task_file_has_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Candidates]\n\n[Done]\n",
                encoding="utf-8",
            )
            fake = FakeTmux()
            decision = run_stop_hook(self.env(task_file, Path(tmpdir) / "missing.json", "MainAgent"), runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress")
        self.assertTrue(any(call[0][:3] == ["tmux", "send-keys", "-t"] for call in fake.calls))

    def test_stop_hook_waits_for_busy_target_to_become_input_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Candidates]\n\n[Done]\n",
                encoding="utf-8",
            )
            fake = BusyThenReadyTmux()
            decision = run_stop_hook(self.env(task_file, Path(tmpdir) / "missing.json", "MainAgent"), runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress")
        self.assertGreaterEqual(fake.capture_count, 8)
        self.assertTrue(any(call[0][:3] == ["tmux", "send-keys", "-t"] for call in fake.calls))

    def test_missing_main_state_accepts_agent_kind_aliases_from_environment(self) -> None:
        for agent_kind in ("main", "main_agent", " MainAgent "):
            with self.subTest(agent_kind=agent_kind):
                with tempfile.TemporaryDirectory() as tmpdir:
                    task_file = Path(tmpdir) / "tasks.ini"
                    task_file.write_text(
                        "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n"
                        "[InReview]\n\n[Candidates]\n\n[Done]\n",
                        encoding="utf-8",
                    )
                    fake = FakeTmux()
                    decision = run_stop_hook(
                        self.env(task_file, Path(tmpdir) / "missing.json", agent_kind),
                        runner=fake,
                    )

                self.assertIsNotNone(decision)
                self.assertTrue(decision.should_wake)
                self.assertEqual(decision.reason, "main_status_progress")

    def test_missing_main_state_stays_quiet_when_task_file_is_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            fake = FakeTmux()
            decision = run_stop_hook(self.env(task_file, Path(tmpdir) / "missing.json", "MainAgent"), runner=fake)

        self.assertIsNotNone(decision)
        self.assertFalse(decision.should_wake)
        self.assertEqual(fake.calls, [])

    def test_main_wakes_when_selfe2e_copy_status_is_progress_despite_task_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            task_file = tmp / "tasks.ini"
            target = tmp / "AgentOrchestra"
            status_file = target / ".tmp" / "self-improvement-e2e" / "status"
            state_file = tmp / "missing.json"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            status_file.parent.mkdir(parents=True)
            status_file.write_text("progress", encoding="utf-8")
            env = self.env(task_file, state_file, "MainAgent")
            env["AGENT_ORCHESTRA_EDIT_ROOT"] = str(target)
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_done_with_selfe2e_status_not_done")
        self.assertTrue(any(call[0][:3] == ["tmux", "send-keys", "-t"] for call in fake.calls))

    def test_missing_professional_state_wakes_stopped_professional_pane(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            fake = FakeTmux()
            decision = run_stop_hook(
                self.env(task_file, Path(tmpdir) / "missing.json", "ProfessionalAgent"),
                runner=fake,
            )

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_agent_state_or_unreadable")
        self.assertTrue(any(call[0][:3] == ["tmux", "send-keys", "-t"] for call in fake.calls))

    def test_missing_professional_state_without_pane_takes_no_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            env = self.env(task_file, Path(tmpdir) / "missing.json", "ProfessionalAgent")
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNone(decision)
        self.assertEqual(fake.calls, [])

    def test_active_professional_without_own_pane_wakes_main_when_task_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            state_file = Path(tmpdir) / "state.json"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            task_file.unlink()
            state_file.write_text(
                '{"agent_id":"agent","agent_kind":"ProfessionalAgent","state":"working"}\n',
                encoding="utf-8",
            )
            env = self.env(task_file, state_file, "ProfessionalAgent")
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "invalid_task_file_or_unreadable_main_fallback")
        self.assertTrue(any(call[0][-2:] == ["%main", "C-m"] for call in fake.calls))

    def test_active_professional_without_own_pane_wakes_main_for_repair(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            state_file = Path(tmpdir) / "state.json"
            task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n"
                "pro-agent: owner_dri=pro-agent; summary=continue scoped work\n\n"
                "[InReview]\n\n[Candidates]\n\n[Done]\n",
                encoding="utf-8",
            )
            state_file.write_text(
                '{"agent_id":"agent","agent_kind":"ProfessionalAgent","state":"working"}\n',
                encoding="utf-8",
            )
            env = self.env(task_file, state_file, "ProfessionalAgent")
            env.pop("AGENT_ORCHESTRA_TMUX_PANE")
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "professional_active_working_main_fallback")
        self.assertTrue(
            any(call[0] == ["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY] for call in fake.calls)
        )

    def test_active_professional_with_invalid_own_pane_wakes_main_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            state_file = Path(tmpdir) / "state.json"
            task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n"
                "pro-agent: owner_dri=pro-agent; summary=continue scoped work\n\n"
                "[InReview]\n\n[Candidates]\n\n[Done]\n",
                encoding="utf-8",
            )
            state_file.write_text(
                '{"agent_id":"agent","agent_kind":"ProfessionalAgent","state":"working"}\n',
                encoding="utf-8",
            )
            env = self.env(task_file, state_file, "ProfessionalAgent")
            env["AGENT_ORCHESTRA_TMUX_PANE"] = ":0.1"
            env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = "%main"
            fake = FakeTmux()
            decision = run_stop_hook(env, runner=fake)

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "professional_active_working_main_fallback")
        self.assertTrue(
            any(call[0] == ["tmux", "send-keys", "-t", "%main", DEFAULT_SUBMIT_KEY] for call in fake.calls)
        )

    def env(self, task_file: Path, state_file: Path, agent_kind: str) -> dict[str, str]:
        return {
            "AGENT_ORCHESTRA_TASK_FILE": str(task_file),
            "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
            "AGENT_ORCHESTRA_AGENT_KIND": agent_kind,
            "AGENT_ORCHESTRA_TMUX_PANE": "%7",
        }


if __name__ == "__main__":
    unittest.main()
