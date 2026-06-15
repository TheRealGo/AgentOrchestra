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
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchMaterialHelperIOTests(unittest.TestCase):
    def test_installed_helper_prepares_professional_launch_material_from_main_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            main = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
                tmux_pane="%main",
            )

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
            pro_state = json.loads((pro_dir / "state.json").read_text(encoding="utf-8"))
            pro_env = json.loads((pro_dir / "env.json").read_text(encoding="utf-8"))
            self.assertEqual(pro_state["state"], "ready")
            self.assertEqual(pro_env["AGENT_ORCHESTRA_TASK_FILE"], str(main.task_file))
            self.assertEqual(pro_env["AGENT_ORCHESTRA_TMUX_PANE"], "%12")
            self.assertEqual(pro_env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"], main.env["AGENT_ORCHESTRA_TMUX_PANE"])
            self.assertEqual(pro_env["PYTHONPATH"], str(pro_dir / "codex_home"))

    def test_installed_helper_preserves_explicit_working_initial_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            main = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
                tmux_pane="%main",
            )

            helper = main.codex_home / "agent_orchestra_minimal" / "prepare_agent_launch.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--agent-id",
                    "pro-explicit-working",
                    "--lead-layer",
                    "15 prompts",
                    "--instruction-text",
                    "Professional layer instruction.",
                    "--tmux-pane",
                    "%12",
                    "--initial-state",
                    "working",
                ],
                env=os.environ | main.env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            pro_state = json.loads(
                (main.run_dir / "agents" / "pro-explicit-working" / "state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(pro_state["state"], "working")

    def test_installed_helper_resolves_protocol_layer_from_main_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target-without-layers"
            target.mkdir()
            with patch.dict(os.environ, {"AGENT_ORCHESTRA_REPO_ROOT": str(ROOT)}, clear=False):
                main = prepare_launch_material(
                    run_dir=Path(tmpdir) / "run",
                    agent_id="main",
                    agent_kind="MainAgent",
                    target_project=target,
                    instruction_text="Main instruction.",
                    tmux_pane="%main",
                )

            helper = main.codex_home / "agent_orchestra_minimal" / "prepare_agent_launch.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--agent-id",
                    "pro-backend",
                    "--protocol-layer",
                    "8",
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
            pro_dir = main.run_dir / "agents" / "pro-backend"
            startup = (pro_dir / "workspace" / "AGENTS.md").read_text(encoding="utf-8")
            pro_env = json.loads((pro_dir / "env.json").read_text(encoding="utf-8"))
            self.assertIn("08_アプリケーション・バックエンド設計", startup)
            self.assertIn("このファイルは `INSTRUCTIONS_template.md`", startup)
            self.assertIn("## Authority Order", startup)
            self.assertEqual(pro_env["AGENT_ORCHESTRA_REPO_ROOT"], str(ROOT))
            self.assertIn(f"export AGENT_ORCHESTRA_REPO_ROOT={ROOT}", (pro_dir / "env.sh").read_text(encoding="utf-8"))

    def test_installed_helper_prefers_protocol_layer_over_target_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            protocol_layer = root / "protocol" / "layers" / "08_protocol"
            target_layer = root / "target" / "layers" / "08_target"
            protocol_layer.mkdir(parents=True)
            target_layer.mkdir(parents=True)
            (protocol_layer / "INSTRUCTIONS.md").write_text("protocol marker\n", encoding="utf-8")
            (target_layer / "INSTRUCTIONS.md").write_text("target contamination marker\n", encoding="utf-8")

            with patch.dict(os.environ, {"AGENT_ORCHESTRA_REPO_ROOT": str(root / "protocol")}, clear=False):
                main = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="main",
                    agent_kind="MainAgent",
                    target_project=root / "target",
                    instruction_text="Main instruction.",
                    tmux_pane="%main",
                )

            helper = main.codex_home / "agent_orchestra_minimal" / "prepare_agent_launch.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--agent-id",
                    "pro-backend",
                    "--protocol-layer",
                    "08",
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
            startup = (main.run_dir / "agents" / "pro-backend" / "workspace" / "AGENTS.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("protocol marker", startup)
            self.assertNotIn("target contamination marker", startup)

    def test_installed_helper_does_not_fallback_to_target_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            protocol = root / "empty-protocol"
            target_layer = root / "target" / "layers" / "08_target"
            protocol.mkdir()
            target_layer.mkdir(parents=True)
            (target_layer / "INSTRUCTIONS.md").write_text("target contamination marker\n", encoding="utf-8")

            with patch.dict(os.environ, {"AGENT_ORCHESTRA_REPO_ROOT": str(protocol)}, clear=False):
                main = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="main",
                    agent_kind="MainAgent",
                    target_project=root / "target",
                    instruction_text="Main instruction.",
                    tmux_pane="%main",
                )

            helper = main.codex_home / "agent_orchestra_minimal" / "prepare_agent_launch.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--agent-id",
                    "pro-backend",
                    "--protocol-layer",
                    "08",
                    "--tmux-pane",
                    "%12",
                ],
                env=os.environ | main.env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("protocol layers directory was not found", result.stderr)

    def test_generated_env_can_run_installed_tmux_send_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-pythonpath",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Module path instruction.",
            )

            result = subprocess.run(
                [
                    material.env["AGENT_ORCHESTRA_PYTHON"],
                    "-m",
                    "agent_orchestra_minimal.tmux_send",
                    "--help",
                ],
                env=os.environ | material.env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("agent-orchestra-tmux-send", result.stdout)


if __name__ == "__main__":
    unittest.main()
