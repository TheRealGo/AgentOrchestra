from __future__ import annotations

import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.claude_settings import (  # noqa: E402
    DEFAULT_PERMISSION_MODE,
    claude_settings,
    trust_seed,
)
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class ClaudeSettingsContractTests(unittest.TestCase):
    def test_settings_registers_stop_hook_with_absolute_command_path(self) -> None:
        hook = Path("/abs/claude_home/hooks/agent_orchestra_stop_hook.py")

        rendered = claude_settings(hook, permission_mode="bypassPermissions")
        data = json.loads(rendered)

        hook_entry = data["hooks"]["Stop"][0]["hooks"][0]
        self.assertEqual(hook_entry["type"], "command")
        self.assertEqual(hook_entry["command"], f"python3 {shlex.quote(str(hook))}")
        self.assertIn(str(hook), hook_entry["command"])
        self.assertEqual(data["permissions"]["defaultMode"], "bypassPermissions")
        # Claude Code has no per-hash hook trust model: settings.json replaces the
        # Codex TOML and carries no trust-hash / trust-level fields.
        self.assertNotIn("trust_level", rendered)
        self.assertNotIn("trusted_hash", rendered)
        self.assertNotIn("hooks.state", rendered)

    def test_settings_defaults_to_bypass_permissions(self) -> None:
        data = json.loads(claude_settings(Path("/abs/hook.py")))

        # bypassPermissions is the default: the team must edit arbitrary repo paths
        # (including .claude/...) unattended, which no scoped allow-list covers.
        self.assertEqual(DEFAULT_PERMISSION_MODE, "bypassPermissions")
        self.assertEqual(data["permissions"]["defaultMode"], DEFAULT_PERMISSION_MODE)

    def test_settings_accepts_overridden_permission_mode(self) -> None:
        data = json.loads(claude_settings(Path("/abs/hook.py"), permission_mode="acceptEdits"))

        self.assertEqual(data["permissions"]["defaultMode"], "acceptEdits")

    def test_settings_carry_no_allow_list(self) -> None:
        # Under bypassPermissions no allow-list is meaningful, so the settings carry
        # only the mode (no inert/dead permission rules).
        data = json.loads(claude_settings(Path("/abs/hook.py")))
        self.assertEqual(set(data["permissions"]), {"defaultMode"})

    def test_trust_seed_preaccepts_workspace_trust_dialog(self) -> None:
        workspace = Path("/abs/run/agents/main/workspace")

        data = json.loads(trust_seed(workspace))

        self.assertTrue(data["hasCompletedOnboarding"])
        project = data["projects"][str(workspace)]
        self.assertTrue(project["hasTrustDialogAccepted"])
        self.assertTrue(project["hasCompletedProjectOnboarding"])
        self.assertEqual(project["projectOnboardingSeenCount"], 1)
        self.assertEqual(project["allowedTools"], [])

    def test_generated_settings_and_trust_seed_stay_valid_json_with_quote_in_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix='agent"orchestra-') as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
            )

            settings_text = material.settings_path.read_text(encoding="utf-8")
            seed_text = (material.claude_config_dir / ".claude.json").read_text(encoding="utf-8")

        self.assertEqual(material.settings_path.name, "settings.json")
        self.assertIn('agent"orchestra-', str(material.workspace))

        # Despite a double quote in the workspace/config path, both generated
        # documents remain valid JSON (the Codex test checked TOML key escaping).
        settings = json.loads(settings_text)
        seed = json.loads(seed_text)

        command = settings["hooks"]["Stop"][0]["hooks"][0]["command"]
        abs_hook = material.claude_config_dir / "hooks" / "agent_orchestra_stop_hook.py"
        self.assertTrue(command.startswith("python3 "))
        self.assertIn(str(abs_hook), command)
        self.assertEqual(settings["permissions"]["defaultMode"], "bypassPermissions")
        self.assertNotIn("allow", settings["permissions"])
        self.assertTrue(seed["projects"][str(material.workspace)]["hasTrustDialogAccepted"])


if __name__ == "__main__":
    unittest.main()
