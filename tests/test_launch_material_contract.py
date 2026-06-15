from __future__ import annotations

import os
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.cli import prepare_main_material  # noqa: E402
from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.task_file import SharedTaskFile  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchMaterialContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.env_patcher = patch.dict(
            os.environ,
            {"AGENT_ORCHESTRA_REPO_ROOT": str(ROOT), "AGENT_ORCHESTRA_TUI_SUBMIT_KEY": ""},
            clear=False,
        )
        self.env_patcher.start()

    def tearDown(self) -> None:
        self.env_patcher.stop()

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
            self.assertIn("--profile", material.command["argv"])
            profile_index = material.command["argv"].index("--profile")
            self.assertEqual(material.command["argv"][profile_index + 1], "agent-orchestra")
            self.assertNotIn("--profile-v2", material.command["argv"])
            self.assertEqual(material.command["config_profile"], "agent-orchestra")
            self.assertNotIn("config_profile_v2", material.command)
            self.assertIn("--ask-for-approval", material.command["argv"])
            approval_index = material.command["argv"].index("--ask-for-approval")
            self.assertEqual(material.command["argv"][approval_index + 1], "on-request")
            self.assertIn("--sandbox", material.command["argv"])
            self.assertIn("--enable", material.command["argv"])
            self.assertIn("--cd", material.command["argv"])
            self.assertIn("--add-dir", material.command["argv"])
            argv = list(material.command["argv"])
            add_dirs = [argv[index + 1] for index, value in enumerate(argv) if value == "--add-dir"]
            self.assertEqual(add_dirs[0], str(ROOT))
            self.assertEqual(material.env["AGENT_ORCHESTRA_TARGET_PROJECT"], str(ROOT))
            self.assertIn(material.env["AGENT_ORCHESTRA_EDIT_ROOT"], add_dirs)
            self.assertNotEqual(material.env["AGENT_ORCHESTRA_EDIT_ROOT"], str(material.run_dir))
            self.assertEqual(material.command["runtime_access_roots"], [str(material.run_dir)])
            self.assertIn(str(material.run_dir), add_dirs)
            self.assertNotIn(
                "Start the agent-orchestra MainAgent run using the loaded AGENTS.md instructions.",
                material.command["argv"],
            )
            self.assertNotIn("Wait for the user request in this Codex CLI session.", startup)
            self.assertNotIn("Current Run Context", startup)
            self.assertNotIn("User task:", startup)
            self.assertNotIn("No task has been provided yet", startup)

    def test_main_agent_startup_uses_progress_task_baseline_without_task_context(self) -> None:
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

            self.assertEqual(task_file.status, "progress")
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
            self.assertIn(
                "generated isolated `AGENTS.md` behavior と選択された layer perspective",
                startup_normalized,
            )
            self.assertNotIn("layer固有の観点で起動する", startup)
            self.assertIn("agent-orchestra の本質", startup)
            self.assertIn("MainAgentが複数のProfessionalAgentを独立環境で立ち上げる", startup)
            self.assertIn("SubAgentはProfessionalAgentの代替ではない", startup)
            self.assertIn("You are a ProfessionalAgent", startup)
            self.assertIn("Use Codex-native SubAgents proactively", startup)
            self.assertIn("Before `ready_for_review`", startup)
            self.assertIn("Do not decide full-run", startup)

    def test_main_agent_startup_surface_states_steward_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
            )

            startup = material.startup_agents.read_text(encoding="utf-8")
            startup_normalized = " ".join(startup.split())
            self.assertIn("You are the MainAgent", startup)
            self.assertIn("the only user-facing Agent and the AgentTeam steward", startup)
            self.assertIn("You do not outrank ProfessionalAgents for editing", startup)
            self.assertIn("change units with an owner/DRI", startup)
            self.assertIn("Integration readiness is a Team decision", startup)
            self.assertIn("`/goal`", startup)
            self.assertIn("current user request", startup)
            self.assertIn("generic \"improve forever\" goal", startup)
            self.assertIn("cycle_done", startup)
            self.assertIn("Continuous goals do not expand user constraints", startup)
            self.assertIn("do not edit outside the user's scope", startup)
            self.assertIn("ProfessionalAgent selection", startup)
            self.assertIn("Choose the ProfessionalAgent team from the user goal", startup)
            self.assertIn("Missing prebuilt `command.json` is not a", " ".join(startup.split()))
            self.assertIn("--profile agent-orchestra", startup)
            self.assertIn("Use Codex-native SubAgents proactively", startup)
            self.assertIn("AgentTeamは必要に応じてtmuxを使用し相互に直接相談する", startup)
            self.assertIn("ProfessionalAgent同士の直接相談は通常の協働経路", startup)
            self.assertIn("tmux通信の具体手順はSkillが担う", startup)
            self.assertIn("配送確認できない通信を成功扱いしない", startup)
            self.assertIn("concrete send/capture/retry procedure", startup_normalized)
            self.assertIn("Runtime側は判断しません", startup)

    def test_launch_material_adds_git_root_when_target_is_nested_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repo"
            target = root / "nested" / "target"
            target.mkdir(parents=True)
            subprocess.run(["git", "init", str(root)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            root = root.resolve()
            target = target.resolve()

            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-git-root",
                agent_kind="ProfessionalAgent",
                target_project=target,
                instruction_text="Layer instruction.",
            )

            argv = list(material.command["argv"])
            add_dirs = [argv[index + 1] for index, value in enumerate(argv) if value == "--add-dir"]
            self.assertEqual(add_dirs[:2], [str(target), str(root)])
            self.assertIn(str(material.run_dir), add_dirs)
            self.assertEqual(material.env["AGENT_ORCHESTRA_TARGET_PROJECT"], str(target))
            self.assertEqual(material.env["AGENT_ORCHESTRA_EDIT_ROOT"], str(root))
            self.assertIn(str(root), material.env["AGENT_ORCHESTRA_ACCESS_ROOTS"])
            startup = material.startup_agents.read_text(encoding="utf-8")
            self.assertIn("Editable/access roots", startup)
            self.assertIn(str(target), startup)
            self.assertIn(str(root), startup)

    def test_professional_agent_startup_surface_states_equal_editing_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-equal-editor",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Professional instruction.",
            )

            startup = material.startup_agents.read_text(encoding="utf-8")
            startup_normalized = " ".join(startup.split())
            self.assertIn("user-facing steward, not your superior", startup)
            self.assertIn("You may edit, propose tasks, review peers, request changes", startup)
            self.assertIn("raise blocking", startup)
            self.assertIn("ready for Team review", startup)
            self.assertIn("scoped task in the shared task file under `[InReview]`", startup)
            self.assertIn("to `[Done]` only when the accepted disposition is known", startup)
            self.assertIn("perform at least one direct peer consultation", startup_normalized)
            self.assertIn("owner/DRI, affected scope, reviewers, required checks", startup)
            self.assertIn("Treat peer consultation as review evidence", startup)
            self.assertIn("integration readiness for a change", startup)
            self.assertIn("Team/DRI review process", startup)
            self.assertIn("concrete delivery procedure", startup_normalized)
            self.assertIn("Do not treat unconfirmed communication as delivered", startup_normalized)

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

    def test_workspace_must_not_have_parent_agents_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            target.mkdir()
            contaminated_parent = root / "outer"
            contaminated_parent.mkdir()
            (contaminated_parent / "AGENTS.md").write_text("parent contamination\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "ancestor AGENTS.md"):
                prepare_launch_material(
                    run_dir=contaminated_parent / "run",
                    agent_id="pro-parent-contaminated",
                    agent_kind="ProfessionalAgent",
                    target_project=target,
                    instruction_text="Layer instruction.",
                )


if __name__ == "__main__":
    unittest.main()
