from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.launch_io import RUNTIME_FILES  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchMaterialInstallContractTests(unittest.TestCase):
    def test_runtime_file_manifest_covers_all_package_modules(self) -> None:
        runtime_dir = ROOT / ".codex" / "agent_orchestra_minimal"
        package_modules = {
            path.name
            for path in runtime_dir.glob("*.py")
            if path.name != "__init__.py"
        }

        self.assertEqual(set(RUNTIME_FILES), package_modules)

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
            for filename in RUNTIME_FILES:
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


if __name__ == "__main__":
    unittest.main()
