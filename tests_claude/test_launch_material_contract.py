from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.cli import prepare_main_material  # noqa: E402
from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.task_file import SharedTaskFile  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchMaterialContractTests(unittest.TestCase):
    def test_start_cli_prepares_main_agent_launch_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_main_material(
                target_project=ROOT,
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                tmux_pane="%1",
            )

            startup = material.startup_claude_md.read_text(encoding="utf-8")
            self.assertIn("Agent kind: `MainAgent`", startup)
            self.assertIn("You are the MainAgent", startup)
            self.assertIn("15_", startup)
            self.assertIn("including any target root `CLAUDE.md`", startup)
            self.assertEqual(material.env["AGENT_ORCHESTRA_TMUX_PANE"], "%1")
            self.assertEqual(material.env["AGENT_ORCHESTRA_PYTHON"], sys.executable)
            self.assertEqual(material.env["AGENT_ORCHESTRA_TUI_SUBMIT_KEY"], "C-m")
            self.assertEqual(material.env["AGENT_ORCHESTRA_PERMISSION_MODE"], "bypassPermissions")
            self.assertNotIn("CODEX_HOME", material.env)

            argv = material.command["argv"]
            self.assertEqual(argv[0], "claude")
            # Two --add-dir: the target project, then the run dir (so the shared
            # tasks.ini / state.json are accessible without a per-file prompt).
            self.assertEqual(argv[1], "--add-dir")
            self.assertEqual(argv[2], str(ROOT))
            self.assertEqual(argv[3], "--add-dir")
            self.assertEqual(argv[4], str(material.run_dir))
            self.assertEqual(argv[5], "--permission-mode")
            self.assertEqual(argv[6], "bypassPermissions")
            for forbidden in ("--profile-v2", "--ask-for-approval", "--sandbox", "--enable", "--cd"):
                self.assertNotIn(forbidden, argv)
            # No synthetic first user prompt (positional) is appended.
            self.assertEqual(len(argv), 7)
            self.assertNotIn("Wait for the user request in this Claude Code session.", startup)
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
            startup = material.startup_claude_md.read_text(encoding="utf-8")

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
            self.assertTrue(material.claude_config_dir.is_dir())
            self.assertNotEqual(material.home, Path.home())
            self.assertNotEqual(material.claude_config_dir, Path.home() / ".claude")
            self.assertTrue((material.workspace / "target_project").is_symlink())

            startup = material.startup_claude_md.read_text(encoding="utf-8")
            startup_normalized = " ".join(startup.split())
            self.assertIn("Layer-specific instruction.", startup)
            self.assertIn("Target project data", startup)
            self.assertIn("target root `CLAUDE.md`, as data/evidence only", startup)
            self.assertIn("Layer `INSTRUCTIONS.md` files define specialist perspective only", startup_normalized)
            self.assertIn("Assigned Specialist Perspective", startup)
            self.assertIn(
                "generated isolated `CLAUDE.md` behavior と選択された layer perspective",
                startup_normalized,
            )
            self.assertNotIn("layer固有の観点で起動する", startup)
            self.assertIn("agent-orchestra の本質", startup)
            self.assertIn("MainAgentが複数のProfessionalAgentを独立環境で立ち上げる", startup)
            self.assertIn("SubAgentはProfessionalAgentの代替ではない", startup)
            self.assertIn("You are a ProfessionalAgent", startup)
            self.assertIn("Use Claude Code subagents (the Task/Agent tool, `.claude/agents`) proactively", startup)
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

            startup = material.startup_claude_md.read_text(encoding="utf-8")
            startup_normalized = " ".join(startup.split())
            self.assertIn("You are the MainAgent", startup)
            self.assertIn("the only user-facing Agent and the AgentTeam steward", startup)
            self.assertIn("You do not outrank ProfessionalAgents for editing", startup)
            self.assertIn("change units with an owner/DRI", startup)
            self.assertIn("Integration readiness is a Team decision", startup)
            self.assertIn("`/goal`", startup)
            self.assertIn("current user request", startup)
            self.assertIn('generic "improve forever"', startup_normalized)
            self.assertIn("cycle_done", startup)
            self.assertIn("Continuous goals do not expand user constraints", startup)
            self.assertIn("do not edit outside the user's scope", startup)
            self.assertIn("ProfessionalAgent selection", startup)
            self.assertIn("Choose the ProfessionalAgent team from the user goal", startup)
            self.assertIn("Missing prebuilt `command.json` is not a", startup_normalized)
            # Claude launch contract replaces Codex `--profile-v2 agent-orchestra`.
            self.assertIn("`--add-dir`", startup)
            self.assertIn("`--permission-mode`", startup)
            self.assertIn("Claude Code has no `--cd`", startup)
            self.assertIn(
                "Use Claude Code subagents (the Task/Agent tool, `.claude/agents`) proactively",
                startup_normalized,
            )
            self.assertIn("AgentTeamは必要に応じてtmuxを使用し相互に直接相談する", startup)
            self.assertIn("ProfessionalAgent同士の直接相談は通常の協働経路", startup)
            self.assertIn("tmux通信の具体手順はSkillが担う", startup)
            self.assertIn("配送確認できない通信を成功扱いしない", startup)
            self.assertIn("concrete send/capture/retry procedure", startup_normalized)
            self.assertIn("Runtime側は判断しません", startup)
            # The malformed-candidate re-kick recovery guidance must survive into
            # the *generated* startup the agent boots from (not only the source
            # templates), and ahead of the large layer embed appended last.
            for phrase in (
                "A Hook wake carries no reason.",
                "the blocker is almost certainly an unresolved `[Candidates]` entry",
                "makes the Hook wake repeat without converging",
                "「open workなし」と報告して止まるだけだと状態が変わらず固定wakeが収束しない",
            ):
                self.assertIn(phrase, startup_normalized)
            layer_embed = startup.find("## Assigned Specialist Perspective")
            recovery_anchor = startup_normalized.find("A Hook wake carries no reason.")
            self.assertGreaterEqual(recovery_anchor, 0)
            self.assertGreaterEqual(layer_embed, 0)
            # Recovery guidance precedes the appended layer INSTRUCTIONS, so the
            # >40k tail-truncation risk falls on the layer embed, not the guidance.
            self.assertLess(
                startup.find("A Hook wake carries no reason."), layer_embed
            )

    def test_professional_agent_startup_surface_states_equal_editing_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-equal-editor",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Professional instruction.",
            )

            startup = material.startup_claude_md.read_text(encoding="utf-8")
            startup_normalized = " ".join(startup.split())
            self.assertIn("user-facing steward, not your superior", startup)
            self.assertIn("You may edit, propose tasks, review peers, request changes", startup)
            self.assertIn("raise blocking", startup)
            self.assertIn("ready for Team review", startup)
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

    def test_workspace_must_not_have_parent_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            target.mkdir()
            contaminated_parent = root / "outer"
            contaminated_parent.mkdir()
            (contaminated_parent / "CLAUDE.md").write_text("parent contamination\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "ancestor CLAUDE.md"):
                prepare_launch_material(
                    run_dir=contaminated_parent / "run",
                    agent_id="pro-parent-contaminated",
                    agent_kind="ProfessionalAgent",
                    target_project=target,
                    instruction_text="Layer instruction.",
                )


if __name__ == "__main__":
    unittest.main()
