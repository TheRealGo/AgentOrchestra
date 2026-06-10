from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.launch_io import RUNTIME_FILES  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchMaterialInstallContractTests(unittest.TestCase):
    def test_runtime_file_manifest_covers_all_package_modules(self) -> None:
        runtime_dir = ROOT / ".claude" / "agent_orchestra_minimal"
        package_modules = {
            path.name
            for path in runtime_dir.glob("*.py")
            if path.name != "__init__.py"
        }

        self.assertEqual(set(RUNTIME_FILES), package_modules)
        self.assertIn("claude_settings.py", RUNTIME_FILES)
        self.assertNotIn("codex_config.py", RUNTIME_FILES)

    def test_launch_material_installs_project_local_hooks_and_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
            )

            settings_text = material.settings_path.read_text(encoding="utf-8")
            settings = json.loads(settings_text)
            self.assertEqual(material.settings_path.name, "settings.json")
            hook_entry = settings["hooks"]["Stop"][0]["hooks"][0]
            hook_target = material.claude_config_dir / "hooks" / "agent_orchestra_stop_hook.py"
            self.assertEqual(hook_entry["type"], "command")
            self.assertTrue(hook_entry["command"].startswith("python3 "))
            self.assertIn(str(hook_target), hook_entry["command"])
            self.assertEqual(settings["permissions"]["defaultMode"], "bypassPermissions")
            # Claude Code settings carry no per-hash hook trust fields.
            self.assertNotIn("trust_level", settings_text)
            self.assertNotIn("trusted_hash", settings_text)
            self.assertNotIn("hooks.state", settings_text)

            self.assertTrue(hook_target.is_file())
            for filename in RUNTIME_FILES:
                self.assertTrue((material.claude_config_dir / "agent_orchestra_minimal" / filename).is_file())
            for template in ("common.CLAUDE.md", "main.CLAUDE.md", "professional.CLAUDE.md"):
                self.assertTrue(
                    (material.claude_config_dir / "agent_orchestra_minimal" / "agent_templates" / template).is_file()
                )
            for skill in (
                "agent-orchestra-launch",
                "agent-orchestra-task-file",
                "agent-orchestra-team",
                "agent-orchestra-tmux-common",
                "agent-orchestra-tmux-main",
            ):
                self.assertTrue((material.claude_config_dir / "skills" / skill / "SKILL.md").is_file())

            # The project trust seed is pre-written to both the isolated HOME and
            # CLAUDE_CONFIG_DIR as .claude.json (not the settings.json).
            for directory in (material.home, material.claude_config_dir):
                seed = json.loads((directory / ".claude.json").read_text(encoding="utf-8"))
                self.assertTrue(seed["hasCompletedOnboarding"])
                self.assertTrue(seed["projects"][str(material.workspace)]["hasTrustDialogAccepted"])

    def test_launch_material_env_and_command_do_not_launch_or_use_claude_print(self) -> None:
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
            self.assertEqual(env["CLAUDE_CONFIG_DIR"], str(material.claude_config_dir))
            self.assertNotIn("CODEX_HOME", env)
            self.assertEqual(env["PYTHONPATH"], str(material.claude_config_dir))
            self.assertEqual(env["AGENT_ORCHESTRA_AGENT_DIR"], str(material.state_file.parent))
            self.assertEqual(env["AGENT_ORCHESTRA_RUN_DIR"], str(material.run_dir))
            self.assertEqual(env["AGENT_ORCHESTRA_AGENT_STATE"], str(material.state_file))
            self.assertEqual(env["AGENT_ORCHESTRA_TASK_FILE"], str(material.task_file))
            self.assertEqual(env["AGENT_ORCHESTRA_PYTHON"], sys.executable)
            self.assertEqual(env["AGENT_ORCHESTRA_TUI_SUBMIT_KEY"], "C-m")
            self.assertEqual(env["AGENT_ORCHESTRA_PERMISSION_MODE"], "bypassPermissions")
            self.assertIn(f"export HOME={material.home}", env_shell)
            self.assertIn(f"export CLAUDE_CONFIG_DIR={material.claude_config_dir}", env_shell)
            self.assertNotIn("export CODEX_HOME=", env_shell)
            self.assertIn(f"export AGENT_ORCHESTRA_AGENT_ID={material.agent_id}", env_shell)
            self.assertIn(f"export AGENT_ORCHESTRA_PYTHON={sys.executable}", env_shell)
            self.assertIn("export AGENT_ORCHESTRA_TUI_SUBMIT_KEY=C-m", env_shell)

            command = json.loads(material.command_path.read_text(encoding="utf-8"))
            argv = command["argv"]
            self.assertEqual(argv[0], "claude")
            self.assertEqual(command["env_shell_file"], str(material.env_shell_path))
            self.assertEqual(command["settings"], str(material.settings_path))
            self.assertIn("--add-dir", argv)
            self.assertIn(str(ROOT), argv)
            self.assertIn("--permission-mode", argv)
            self.assertIn("bypassPermissions", argv)
            for forbidden in (
                "--profile-v2",
                "--ask-for-approval",
                "--sandbox",
                "--enable",
                "--cd",
                "-p",
                "--print",
                "exec",
            ):
                self.assertNotIn(forbidden, argv)
            self.assertNotIn("shell_command", command)
            self.assertTrue(command["does_not_launch"])
            self.assertFalse((material.state_file.parent / "shell_command.txt").exists())


if __name__ == "__main__":
    unittest.main()
