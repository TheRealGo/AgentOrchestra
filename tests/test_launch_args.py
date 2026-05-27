from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.cli import current_tmux_pane  # noqa: E402
from agent_orchestra_minimal.launch_args import main_tmux_pane  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchArgsTests(unittest.TestCase):
    def test_launch_material_rejects_codex_args_that_look_like_initial_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_args = (
                ("--", "fix"),
                ("fix", "launcher"),
                ("exec", "echo ok"),
                ("--profile", "agent-orchestra"),
                ("--profile-v2", "agent-orchestra"),
                ("--cd", str(ROOT)),
                ("--add-dir", str(ROOT)),
                ("--dangerously-bypass-hook-trust",),
                ("--dangerously-bypass-approvals-and-sandbox",),
                ("-c", "sandbox_mode=danger-full-access"),
                ("-c", "hooks.enabled=false"),
                ("--model", "--cd"),
                ("--model", "--"),
                ("--model", "--no-alt-screen"),
                ("-m", "--add-dir"),
                ("-c", "--no-alt-screen"),
            )
            for codex_args in bad_args:
                with self.subTest(codex_args=codex_args):
                    with self.assertRaisesRegex(ValueError, "codex_args"):
                        prepare_launch_material(
                            run_dir=Path(tmpdir) / "run",
                            agent_id="pro-bad-argv",
                            agent_kind="ProfessionalAgent",
                            target_project=ROOT,
                            instruction_text="Docs instruction.",
                            codex_args=codex_args,
                        )

    def test_launch_material_accepts_narrow_safe_codex_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-safe-argv",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Docs instruction.",
                codex_args=("--model", "gpt-5.5", "--no-alt-screen", "-c", "model_reasoning_effort=high"),
            )

        argv = material.command["argv"]
        self.assertIn("--model", argv)
        self.assertIn("--no-alt-screen", argv)
        self.assertIn("model_reasoning_effort=high", argv)

    def test_professional_main_pane_requires_explicit_main_pane_environment(self) -> None:
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_TMUX_PANE": "%caller"}, clear=True):
            self.assertIsNone(main_tmux_pane("ProfessionalAgent", "%pro"))

        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": "%main"}, clear=True):
            self.assertEqual(main_tmux_pane("ProfessionalAgent", "%pro"), "%main")

    def test_blank_tmux_pane_values_are_not_written_as_deterministic_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-blank-pane",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Docs instruction.",
                tmux_pane="   ",
            )
            state = AgentState.read(material.state_file)

        self.assertNotIn("AGENT_ORCHESTRA_TMUX_PANE", material.env)
        self.assertIsNone(state.tmux_target)

    def test_main_pane_environment_is_trimmed_and_blank_values_are_ignored(self) -> None:
        self.assertEqual(main_tmux_pane("MainAgent", "  %main  "), "%main")
        self.assertIsNone(main_tmux_pane("MainAgent", "   "))
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": "  %main  "}, clear=True):
            self.assertEqual(main_tmux_pane("ProfessionalAgent", "%pro"), "%main")
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": "   "}, clear=True):
            self.assertIsNone(main_tmux_pane("ProfessionalAgent", "%pro"))

    def test_tmux_pane_values_must_be_deterministic_pane_ids(self) -> None:
        for value in ("1", ":0.1", "%main other", "%main\nother"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "tmux pane"):
                main_tmux_pane("MainAgent", value)
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": ":0.1"}, clear=True):
            with self.assertRaisesRegex(ValueError, "tmux pane"):
                main_tmux_pane("ProfessionalAgent", "%pro")

    def test_current_tmux_pane_does_not_infer_from_active_client_pane(self) -> None:
        with patch.dict(os.environ, {"TMUX": "/tmp/tmux-123/default,1,0"}, clear=True):
            with patch("agent_orchestra_minimal.cli.pane_from_current_tty", return_value=None):
                with patch("agent_orchestra_minimal.cli.subprocess.run") as run:
                    pane = current_tmux_pane()

        self.assertIsNone(pane)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
