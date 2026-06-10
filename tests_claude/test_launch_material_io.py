from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))
from agent_orchestra_minimal.cli import prepare_main_material  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchMaterialIOTests(unittest.TestCase):
    def test_main_material_uses_protocol_layer_before_target_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            layer = target / "layers" / "15_target_layer"
            layer.mkdir(parents=True)
            (layer / "INSTRUCTIONS.md").write_text("target contamination marker\n", encoding="utf-8")

            material = prepare_main_material(
                target_project=target,
                run_dir=root / "run",
                agent_id="main",
                tmux_pane="%1",
            )

            startup = material.startup_claude_md.read_text(encoding="utf-8")
            self.assertNotIn("target contamination marker", startup)
            self.assertIn("15_開発プロセス・品質保証・CI・CD・リリース", startup)
            self.assertIn("AgentTeamのsteward", startup)
            self.assertIn("編集・提案・レビュー・差し戻し・blocking objectionはAgentTeam共通の権限", startup)
            self.assertIn("change units with an owner/DRI", startup)

    def test_main_material_does_not_fallback_to_target_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            protocol = root / "empty-protocol"
            target_layer = root / "target" / "layers" / "15_target_layer"
            protocol.mkdir()
            target_layer.mkdir(parents=True)
            (target_layer / "INSTRUCTIONS.md").write_text("target marker\n", encoding="utf-8")

            with patch.dict(os.environ, {"AGENT_ORCHESTRA_REPO_ROOT": str(protocol)}, clear=False):
                with self.assertRaisesRegex(FileNotFoundError, "protocol layer 15"):
                    prepare_main_material(
                        target_project=root / "target",
                        run_dir=root / "run",
                        agent_id="main",
                        tmux_pane="%1",
                    )

    def test_main_material_preserves_protocol_root_without_nix_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            target.mkdir()

            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("AGENT_ORCHESTRA_REPO_ROOT", None)
                material = prepare_main_material(
                    target_project=target,
                    run_dir=root / "run",
                    agent_id="main",
                    tmux_pane="%1",
                )

            self.assertEqual(material.env["AGENT_ORCHESTRA_REPO_ROOT"], str(ROOT))
            self.assertIn(f"export AGENT_ORCHESTRA_REPO_ROOT={ROOT}", material.env_shell_path.read_text(encoding="utf-8"))

    def test_launch_material_preserves_configured_tui_submit_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "C-x"}, clear=False):
                material = prepare_launch_material(
                    run_dir=Path(tmpdir) / "run",
                    agent_id="pro-submit-key",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="Submit key instruction.",
                )

            env = json.loads(material.env_path.read_text(encoding="utf-8"))
            env_shell = material.env_shell_path.read_text(encoding="utf-8")
            self.assertEqual(env["AGENT_ORCHESTRA_TUI_SUBMIT_KEY"], "C-x")
            self.assertIn("export AGENT_ORCHESTRA_TUI_SUBMIT_KEY=C-x", env_shell)

    def test_main_material_prefers_explicit_main_pane_over_inherited_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(
                os.environ,
                {
                    "AGENT_ORCHESTRA_MAIN_TMUX_PANE": "%old-main",
                    "AGENT_ORCHESTRA_TMUX_PANE": "%caller",
                },
                clear=False,
            ):
                material = prepare_main_material(
                    target_project=ROOT,
                    run_dir=Path(tmpdir) / "run",
                    agent_id="main",
                    tmux_pane="%new-main",
                )

        self.assertEqual(material.env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"], "%new-main")

    def test_target_project_link_is_refreshed_when_reusing_agent_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first_target = root / "first-target"
            second_target = root / "second-target"
            first_target.mkdir()
            second_target.mkdir()
            run_dir = root / "run"

            first = prepare_launch_material(
                run_dir=run_dir,
                agent_id="main",
                agent_kind="MainAgent",
                target_project=first_target,
                instruction_text="First instruction.",
            )
            self.assertEqual((first.workspace / "target_project").resolve(), first_target.resolve())

            second = prepare_launch_material(
                run_dir=run_dir,
                agent_id="main",
                agent_kind="MainAgent",
                target_project=second_target,
                instruction_text="Second instruction.",
            )
            self.assertEqual((second.workspace / "target_project").resolve(), second_target.resolve())

    def test_reused_launch_material_keeps_home_claude_config_and_workspace_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            target.mkdir()
            run_dir = root / "run"
            first = prepare_launch_material(
                run_dir=run_dir,
                agent_id="pro-clean",
                agent_kind="ProfessionalAgent",
                target_project=target,
                instruction_text="First instruction.",
            )
            (first.home / "stale-home").write_text("old home\n", encoding="utf-8")
            (first.claude_config_dir / "stale-claude").write_text("old claude\n", encoding="utf-8")
            (first.workspace / "stale-workspace").write_text("old workspace\n", encoding="utf-8")
            second = prepare_launch_material(
                run_dir=run_dir,
                agent_id="pro-clean",
                agent_kind="ProfessionalAgent",
                target_project=target,
                instruction_text="Second instruction.",
            )
            self.assertFalse((second.home / "stale-home").exists())
            self.assertFalse((second.claude_config_dir / "stale-claude").exists())
            self.assertFalse((second.workspace / "stale-workspace").exists())
            self.assertIn("Second instruction.", second.startup_claude_md.read_text(encoding="utf-8"))

    def test_reused_launch_material_cleans_stale_isolated_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            stale_target = root / "stale-target"
            for path in (target, stale_target):
                path.mkdir()
            run_dir = root / "run"
            agent_dir = run_dir / "agents" / "pro-symlink-clean"
            agent_dir.mkdir(parents=True)
            for name in ("workspace", "home", "claude_home"):
                os.symlink(stale_target, agent_dir / name, target_is_directory=True)

            material = prepare_launch_material(
                run_dir=run_dir,
                agent_id="pro-symlink-clean",
                agent_kind="ProfessionalAgent",
                target_project=target,
                instruction_text="Clean stale symlinks.",
            )

            for path in (material.workspace, material.home, material.claude_config_dir):
                self.assertTrue(path.is_dir())
                self.assertFalse(path.is_symlink())
            self.assertTrue(stale_target.is_dir())

    def test_professional_startup_material_encodes_equal_editing_team_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-team-contract",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Professional layer instruction.",
            )

            startup = material.startup_claude_md.read_text(encoding="utf-8")
            startup_normalized = " ".join(startup.split())
            self.assertIn("user-facing steward, not your superior", startup)
            self.assertIn("You may edit, propose tasks, review peers, request changes, and raise blocking", startup)
            self.assertIn("perform at least one direct peer consultation", startup_normalized)
            self.assertIn("Treat peer consultation as review evidence", startup)
            self.assertIn("concrete delivery procedure", startup_normalized)
            self.assertIn("Do not treat unconfirmed communication as delivered", startup_normalized)


if __name__ == "__main__":
    unittest.main()
