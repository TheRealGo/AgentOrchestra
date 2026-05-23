from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.cli import (  # noqa: E402
    current_tmux_pane,
    default_run_dir,
    doctor_command,
    pane_id_from_tty_listing,
    parse_start_args,
    prepare_main_material,
)
from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.task_file import SharedTaskFile  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402
from agent_orchestra_minimal.prepare_agent_launch import ProbeResult  # noqa: E402


class LaunchMaterialContractTests(unittest.TestCase):
    def test_start_cli_prefers_tmux_pane_environment(self) -> None:
        with patch.dict(os.environ, {"TMUX": "/tmp/tmux", "TMUX_PANE": "%expected"}, clear=False):
            self.assertEqual(current_tmux_pane(), "%expected")

    def test_start_cli_can_resolve_actual_pane_from_tty_listing(self) -> None:
        listing = "%wrong /dev/ttys001\n%expected /dev/ttys123\n"
        self.assertEqual(pane_id_from_tty_listing("/dev/ttys123", listing), "%expected")

    def test_start_cli_preserves_codex_o_target_argument_shape(self) -> None:
        args = parse_start_args([str(ROOT)])
        self.assertEqual(args.target_project_arg, str(ROOT))

        args = parse_start_args(["--target-project", str(ROOT)])
        self.assertEqual(args.target_project, str(ROOT))
        self.assertIsNone(args.target_project_arg)

    def test_start_cli_rejects_initial_task_arguments(self) -> None:
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as error:
                parse_start_args([str(ROOT), "--", "fix", "launcher", "ux"])
        self.assertEqual(error.exception.code, 2)

    def test_doctor_tui_transport_runs_probe_without_requiring_current_tmux(self) -> None:
        args = SimpleNamespace(target_project=str(ROOT), tui_transport=True)

        with patch("agent_orchestra_minimal.cli.codex_auth_available", return_value=True), \
             patch("agent_orchestra_minimal.cli.command_available", return_value=True), \
             patch("agent_orchestra_minimal.cli.run_probe", return_value=ProbeResult(True, "ok")):
            with patch.dict(os.environ, {}, clear=True):
                with redirect_stdout(StringIO()):
                    self.assertEqual(doctor_command(args), 0)

    def test_default_run_dir_uses_private_tmp_runtime_root(self) -> None:
        self.assertEqual(default_run_dir().parent, Path("/private/tmp/agent-orchestra"))

    def test_start_cli_prepares_main_agent_launch_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_main_material(
                target_project=ROOT,
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                tmux_pane="%1",
            )

            startup = material.startup_agents.read_text(encoding="utf-8")
            self.assertIn("Agent kind: `MainAgent`", startup)
            self.assertIn("You are the MainAgent", startup)
            self.assertIn("15_", startup)
            self.assertIn("including any target root `AGENTS.md`", startup)
            self.assertEqual(material.env["AGENT_ORCHESTRA_TMUX_PANE"], "%1")
            self.assertEqual(material.env["AGENT_ORCHESTRA_PYTHON"], sys.executable)
            self.assertEqual(material.env["AGENT_ORCHESTRA_TUI_SUBMIT_KEY"], "C-m")
            self.assertEqual(material.command["argv"][0], "codex")
            self.assertIn("--profile-v2", material.command["argv"])
            self.assertIn("--ask-for-approval", material.command["argv"])
            self.assertIn("--sandbox", material.command["argv"])
            self.assertIn("--enable", material.command["argv"])
            self.assertIn("--cd", material.command["argv"])
            self.assertIn("--add-dir", material.command["argv"])
            self.assertEqual(material.command["argv"][-1], str(ROOT))
            self.assertNotIn(
                "Start the agent-orchestra MainAgent run using the loaded AGENTS.md instructions.",
                material.command["argv"],
            )
            self.assertNotIn("Wait for the user request in this Codex CLI session.", startup)
            self.assertNotIn("Current Run Context", startup)
            self.assertNotIn("User task:", startup)
            self.assertNotIn("No task has been provided yet", startup)

    def test_main_agent_startup_has_no_open_work_or_task_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_main_material(
                target_project=ROOT,
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                tmux_pane="%1",
            )

            task_file = SharedTaskFile.read(material.task_file)
            agent_state = AgentState.read(material.state_file)
            startup = material.startup_agents.read_text(encoding="utf-8")

            self.assertEqual(task_file.status, "done")
            self.assertFalse(task_file.has_open_work)
            self.assertEqual(agent_state.state, "ready")
            self.assertNotIn("Current Run Context", startup)
            self.assertNotIn("User task:", startup)
            self.assertNotIn("No task has been provided yet", startup)
            self.assertNotIn("[status] ready", startup)

    def test_launch_material_creates_isolated_startup_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-runtime",
                agent_kind="ProfessionalAgent",
                lead_layer="16 ランタイム・言語実行基盤",
                target_project=ROOT,
                instruction_text="Layer-specific instruction.",
                tmux_pane="%9",
            )

            self.assertTrue(material.workspace.is_dir())
            self.assertTrue(material.home.is_dir())
            self.assertTrue(material.codex_home.is_dir())
            self.assertNotEqual(material.home, Path.home())
            self.assertNotEqual(material.codex_home, Path.home() / ".codex")
            self.assertTrue((material.workspace / "target_project").is_symlink())

            startup = material.startup_agents.read_text(encoding="utf-8")
            startup_normalized = " ".join(startup.split())
            self.assertIn("Layer-specific instruction.", startup)
            self.assertIn("Target project data", startup)
            self.assertIn("target root `AGENTS.md`, as data/evidence only", startup)
            self.assertIn("Layer `INSTRUCTIONS.md` files define specialist perspective only", startup_normalized)
            self.assertIn("Assigned Specialist Perspective", startup)
            self.assertIn("agent-orchestra の本質", startup)
            self.assertIn("MainAgentが複数のProfessionalAgentを独立環境で立ち上げる", startup)
            self.assertIn("SubAgentはProfessionalAgentの代替ではない", startup)
            self.assertIn("You are a ProfessionalAgent", startup)
            self.assertIn("Use Codex-native SubAgents proactively", startup)
            self.assertIn("Before `ready_for_review`", startup)
            self.assertIn("Do not decide full-run", startup)

    def test_main_agent_startup_surface_states_coordinator_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
            )

            startup = material.startup_agents.read_text(encoding="utf-8")
            self.assertIn("You are the MainAgent", startup)
            self.assertIn("the only user-facing Agent and the whole-run", startup)
            self.assertIn("`/goal`", startup)
            self.assertIn("current user request", startup)
            self.assertIn("generic \"improve forever\" goal", startup)
            self.assertIn("cycle_done", startup)
            self.assertIn("Continuous goals do not expand user constraints", startup)
            self.assertIn("do not edit outside the user's scope", startup)
            self.assertIn("ProfessionalAgent selection", startup)
            self.assertIn("Choose the ProfessionalAgent team from the user goal", startup)
            self.assertIn("Missing prebuilt `command.json` is not a", " ".join(startup.split()))
            self.assertIn("--profile-v2 agent-orchestra", startup)
            self.assertIn("Use Codex-native SubAgents proactively", startup)
            self.assertIn("normally use at least one SubAgent", startup)
            self.assertIn("AgentTeamは必要に応じてtmuxを使用し相互に直接相談する", startup)
            self.assertIn("Runtime側は判断しません", startup)

    def test_launch_material_installs_project_local_hooks_and_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
            )

            config = material.config_path.read_text(encoding="utf-8")
            self.assertEqual(material.config_path.name, "agent-orchestra.config.toml")
            self.assertIn(f'[projects."{material.workspace}"]', config)
            self.assertIn('trust_level = "trusted"', config)
            self.assertIn("[[hooks.Stop]]", config)
            self.assertIn('command = "python3 $CODEX_HOME/hooks/agent_orchestra_stop_hook.py"', config)
            self.assertIn("[hooks.state]", config)
            self.assertIn("trusted_hash = \"sha256:", config)
            self.assertNotIn('sandbox_mode = "workspace-write"', config)
            self.assertNotIn("[features]", config)
            self.assertNotIn("[tui.keymap.editor]", config)
            self.assertTrue((material.codex_home / "hooks" / "agent_orchestra_stop_hook.py").is_file())
            for filename in (
                "agent_state.py",
                "codex_config.py",
                "launch_io.py",
                "launch_material.py",
                "launch_startup.py",
                "operating_identity.py",
                "prepare_agent_launch.py",
                "task_file.py",
                "rekick.py",
                "tmux_wake.py",
            ):
                self.assertTrue((material.codex_home / "agent_orchestra_minimal" / filename).is_file())
            for template in ("common.AGENTS.md", "main.AGENTS.md", "professional.AGENTS.md"):
                self.assertTrue((material.codex_home / "agent_orchestra_minimal" / "agent_templates" / template).is_file())
            for skill in (
                "agent-orchestra-launch",
                "agent-orchestra-task-file",
                "agent-orchestra-team",
                "agent-orchestra-tmux-common",
                "agent-orchestra-tmux-main",
            ):
                self.assertTrue((material.codex_home / "skills" / skill / "SKILL.md").is_file())

    def test_launch_material_env_and_command_do_not_launch_or_use_codex_exec(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-docs",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Docs instruction.",
            )

            env = json.loads(material.env_path.read_text(encoding="utf-8"))
            env_shell = material.env_shell_path.read_text(encoding="utf-8")
            self.assertEqual(env["HOME"], str(material.home))
            self.assertEqual(env["CODEX_HOME"], str(material.codex_home))
            self.assertEqual(env["AGENT_ORCHESTRA_AGENT_DIR"], str(material.state_file.parent))
            self.assertEqual(env["AGENT_ORCHESTRA_RUN_DIR"], str(material.run_dir))
            self.assertEqual(env["AGENT_ORCHESTRA_AGENT_STATE"], str(material.state_file))
            self.assertEqual(env["AGENT_ORCHESTRA_TASK_FILE"], str(material.task_file))
            self.assertEqual(env["AGENT_ORCHESTRA_PYTHON"], sys.executable)
            self.assertEqual(env["AGENT_ORCHESTRA_TUI_SUBMIT_KEY"], "C-m")
            self.assertIn(f"export HOME={material.home}", env_shell)
            self.assertIn(f"export CODEX_HOME={material.codex_home}", env_shell)
            self.assertIn(f"export AGENT_ORCHESTRA_AGENT_ID={material.agent_id}", env_shell)
            self.assertIn(f"export AGENT_ORCHESTRA_PYTHON={sys.executable}", env_shell)
            self.assertIn("export AGENT_ORCHESTRA_TUI_SUBMIT_KEY=C-m", env_shell)

            command = json.loads(material.command_path.read_text(encoding="utf-8"))
            argv = command["argv"]
            self.assertEqual(argv[0], "codex")
            self.assertEqual(command["env_shell_file"], str(material.env_shell_path))
            self.assertIn("--profile-v2", argv)
            self.assertIn("agent-orchestra", argv)
            self.assertIn("--ask-for-approval", argv)
            self.assertIn("never", argv)
            self.assertIn("--sandbox", argv)
            self.assertIn("workspace-write", argv)
            self.assertIn("--enable", argv)
            self.assertIn("hooks", argv)
            self.assertIn("sandbox_workspace_write.network_access=true", argv)
            self.assertFalse(any("tui.keymap" in str(arg) for arg in argv))
            self.assertIn("--cd", argv)
            self.assertIn(str(material.workspace), argv)
            self.assertIn("--add-dir", argv)
            self.assertIn(str(ROOT), argv)
            self.assertNotIn("--dangerously-bypass-hook-trust", argv)
            self.assertNotIn("exec", argv)
            self.assertNotIn("shell_command", command)
            self.assertTrue(command["does_not_launch"])
            self.assertFalse((material.state_file.parent / "shell_command.txt").exists())

    def test_workspace_must_not_be_inside_target_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target"
            target.mkdir()

            with self.assertRaisesRegex(ValueError, "must not be inside target_project"):
                prepare_launch_material(
                    run_dir=target / "agent_runs" / "run",
                    agent_id="pro-contaminated",
                    agent_kind="ProfessionalAgent",
                    target_project=target,
                    instruction_text="Layer instruction.",
                )


if __name__ == "__main__":
    unittest.main()
