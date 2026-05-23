from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

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

            startup = material.startup_agents.read_text(encoding="utf-8")
            self.assertNotIn("target contamination marker", startup)
            self.assertIn("15_開発プロセス・品質保証・CI・CD・リリース", startup)

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

    def test_reused_launch_material_keeps_home_codex_home_and_workspace_clean(self) -> None:
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
            (first.codex_home / "stale-codex").write_text("old codex\n", encoding="utf-8")
            (first.workspace / "stale-workspace").write_text("old workspace\n", encoding="utf-8")
            second = prepare_launch_material(
                run_dir=run_dir,
                agent_id="pro-clean",
                agent_kind="ProfessionalAgent",
                target_project=target,
                instruction_text="Second instruction.",
            )
            self.assertFalse((second.home / "stale-home").exists())
            self.assertFalse((second.codex_home / "stale-codex").exists())
            self.assertFalse((second.workspace / "stale-workspace").exists())
            self.assertIn("Second instruction.", second.startup_agents.read_text(encoding="utf-8"))

    def test_target_project_link_refuses_non_symlink_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            target.mkdir()
            collision = root / "run" / "agents" / "main" / "workspace" / "target_project"
            collision.mkdir(parents=True)

            with self.assertRaisesRegex(FileExistsError, "not a symlink"):
                prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="main",
                    agent_kind="MainAgent",
                    target_project=target,
                    instruction_text="Instruction.",
                )

    def test_installed_helper_prepares_professional_launch_material_from_main_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            main = prepare_launch_material(
                run_dir=Path(tmpdir) / "run", agent_id="main", agent_kind="MainAgent",
                target_project=ROOT, instruction_text="Main instruction.", tmux_pane="%main")

            helper = main.codex_home / "agent_orchestra_minimal" / "prepare_agent_launch.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--agent-id",
                    "pro-spec-review",
                    "--lead-layer",
                    "15 prompts",
                    "--instruction-text",
                    "Professional layer instruction.",
                    "--tmux-pane",
                    "%12",
                ],
                env=os.environ | main.env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("command_json=", result.stdout)
            pro_dir = main.run_dir / "agents" / "pro-spec-review"
            self.assertTrue((pro_dir / "command.json").is_file())
            self.assertTrue((pro_dir / "env.json").is_file())
            self.assertTrue((pro_dir / "env.sh").is_file())
            pro_env = json.loads((pro_dir / "env.json").read_text(encoding="utf-8"))
            self.assertEqual(pro_env["AGENT_ORCHESTRA_TASK_FILE"], str(main.task_file))
            self.assertEqual(pro_env["AGENT_ORCHESTRA_TMUX_PANE"], "%12")
            self.assertEqual(pro_env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"], main.env["AGENT_ORCHESTRA_TMUX_PANE"])

    def test_launch_material_copies_auth_without_copying_user_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_home = Path(tmpdir) / "source_codex"
            source_home.mkdir()
            auth_source = source_home / "auth.json"
            auth_source.write_text('{"token":"redacted-test-token"}\n', encoding="utf-8")
            (source_home / "AGENTS.md").write_text("must not copy\n", encoding="utf-8")
            (source_home / "config.toml").write_text("must not copy\n", encoding="utf-8")

            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-auth",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Auth bridge instruction.",
                auth_source=auth_source,
            )

            copied_auth = material.codex_home / "auth.json"
            self.assertEqual(copied_auth.read_text(encoding="utf-8"), auth_source.read_text(encoding="utf-8"))
            self.assertEqual(copied_auth.stat().st_mode & 0o777, 0o600)
            self.assertFalse((material.codex_home / "AGENTS.md").exists())
            self.assertNotEqual(material.config_path.read_text(encoding="utf-8"), "must not copy\n")

    def test_nested_launch_material_defaults_to_current_codex_home_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            current_codex_home = tmp / "current_codex_home"
            current_codex_home.mkdir()
            current_auth = current_codex_home / "auth.json"
            current_auth.write_text('{"token":"nested-runtime-token"}\n', encoding="utf-8")

            old_codex_home = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = str(current_codex_home)
            try:
                material = prepare_launch_material(
                    run_dir=tmp / "run",
                    agent_id="nested-pro-auth",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="Nested auth instruction.",
                )
            finally:
                if old_codex_home is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = old_codex_home

            copied_auth = material.codex_home / "auth.json"
            self.assertEqual(copied_auth.read_text(encoding="utf-8"), current_auth.read_text(encoding="utf-8"))
            self.assertEqual(copied_auth.stat().st_mode & 0o777, 0o600)

    def test_generated_stop_hook_runs_from_isolated_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_bin = tmp / "bin"
            fake_bin.mkdir()
            calls = tmp / "tmux_calls.txt"
            fake_tmux = fake_bin / "tmux"
            fake_tmux.write_text(
                "#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' \"$*\" >> \"$AO_TMUX_CALLS\"\nexit 0\n",
                encoding="utf-8",
            )
            fake_tmux.chmod(0o755)

            material = prepare_launch_material(
                run_dir=tmp / "run",
                agent_id="main-hook",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Hook smoke instruction.",
                tmux_pane="%7",
            )
            material.task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Done]\n",
                encoding="utf-8",
            )
            env = os.environ | material.env | {
                "AO_TMUX_CALLS": str(calls),
                "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
            }
            result = subprocess.run(
                [material.env["AGENT_ORCHESTRA_PYTHON"], str(material.codex_home / "hooks" / "agent_orchestra_stop_hook.py")],
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertIn("send-keys -t %7 C-m", calls.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
