from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402
from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from agent_orchestra_minimal.tmux_wake import DEFAULT_SUBMIT_KEY, run_stop_hook  # noqa: E402
from stop_hook_helpers import FakeTmux, NoWakeSleepMixin  # noqa: E402


class SubmitKeyDefaultTests(NoWakeSleepMixin, unittest.TestCase):
    def test_launch_material_defaults_blank_tui_submit_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "  "}, clear=False):
                material = prepare_launch_material(
                    run_dir=Path(tmpdir) / "run",
                    agent_id="pro-blank-submit-key",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="Submit key instruction.",
                )

            env = json.loads(material.env_path.read_text(encoding="utf-8"))
            env_shell = material.env_shell_path.read_text(encoding="utf-8")
            self.assertEqual(env["AGENT_ORCHESTRA_TUI_SUBMIT_KEY"], DEFAULT_SUBMIT_KEY)
            self.assertIn(f"export AGENT_ORCHESTRA_TUI_SUBMIT_KEY={DEFAULT_SUBMIT_KEY}", env_shell)

    def test_stop_hook_defaults_blank_submit_key_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_file = root / "tasks.ini"
            state_file = root / "state.json"
            task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Candidates]\n\n[Done]\n",
                encoding="utf-8",
            )
            AgentState(state="working", agent_id="main", agent_kind="MainAgent", tmux_target="%7").write(state_file)
            fake = FakeTmux()
            decision = run_stop_hook(
                {
                    "AGENT_ORCHESTRA_TASK_FILE": str(task_file),
                    "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
                    "AGENT_ORCHESTRA_TMUX_PANE": "%7",
                    "AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "  ",
                },
                runner=fake,
            )

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(fake.calls[-3], (["tmux", "send-keys", "-t", "%7", DEFAULT_SUBMIT_KEY], None))

    def test_launch_material_rejects_invalid_tui_submit_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "C-m Space"}, clear=False):
                with self.assertRaisesRegex(ValueError, "submit_key"):
                    prepare_launch_material(
                        run_dir=Path(tmpdir) / "run",
                        agent_id="pro-invalid-submit-key",
                        agent_kind="ProfessionalAgent",
                        target_project=ROOT,
                        instruction_text="Submit key instruction.",
                    )

    def test_tmux_send_rejects_invalid_submit_key_token(self) -> None:
        fake = FakeTmux()

        with self.assertRaisesRegex(ValueError, "submit_key"):
            send_text("%7", "MainAgent: review", submit_key="C-m Space", runner=fake)

        self.assertEqual(fake.calls, [])

    def test_stop_hook_reports_delivery_failure_for_invalid_submit_key_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_file = root / "tasks.ini"
            state_file = root / "state.json"
            task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Candidates]\n\n[Done]\n",
                encoding="utf-8",
            )
            AgentState(state="working", agent_id="main", agent_kind="MainAgent", tmux_target="%7").write(state_file)
            fake = FakeTmux()
            decision = run_stop_hook(
                {
                    "AGENT_ORCHESTRA_TASK_FILE": str(task_file),
                    "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
                    "AGENT_ORCHESTRA_TMUX_PANE": "%7",
                    "AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "C-m Space",
                },
                runner=fake,
            )

        self.assertIsNotNone(decision)
        self.assertTrue(decision.should_wake)
        self.assertEqual(decision.reason, "main_status_progress_wake_delivery_failed")
        self.assertEqual(fake.calls, [])


if __name__ == "__main__":
    unittest.main()
