from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"
sys.path.insert(0, str(CODEX))


class RuntimeBoundaryTests(unittest.TestCase):
    def test_runtime_owned_codex_tree_contains_required_runtime_material(self) -> None:
        required = {
            "agent_orchestra_minimal/agent_state.py",
            "agent_orchestra_minimal/candidate_ledger.py",
            "agent_orchestra_minimal/agent_templates/common.AGENTS.md",
            "agent_orchestra_minimal/agent_templates/main.AGENTS.md",
            "agent_orchestra_minimal/agent_templates/professional.AGENTS.md",
            "agent_orchestra_minimal/cli.py",
            "agent_orchestra_minimal/codex_config.py",
            "agent_orchestra_minimal/doctor.py",
            "agent_orchestra_minimal/launch_material.py",
            "agent_orchestra_minimal/launch_io.py",
            "agent_orchestra_minimal/launch_startup.py",
            "agent_orchestra_minimal/launch_args.py",
            "agent_orchestra_minimal/operating_identity.py",
            "agent_orchestra_minimal/prepare_agent_launch.py",
            "agent_orchestra_minimal/rekick.py",
            "agent_orchestra_minimal/task_file.py",
            "agent_orchestra_minimal/tmux_delivery.py",
            "agent_orchestra_minimal/tmux_targets.py",
            "agent_orchestra_minimal/tmux_wake.py",
            "bin/codex-o",
            "hooks/agent_orchestra_stop_hook.py",
            "skills/agent-orchestra-launch/SKILL.md",
            "skills/agent-orchestra-task-file/SKILL.md",
            "skills/agent-orchestra-team/SKILL.md",
            "skills/agent-orchestra-tmux-common/SKILL.md",
            "skills/agent-orchestra-tmux-main/SKILL.md",
        }
        actual = {
            str(path.relative_to(CODEX))
            for root in (
                CODEX / "agent_orchestra_minimal",
                CODEX / "bin",
                CODEX / "hooks",
                CODEX / "skills",
            )
            for path in root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
            and ".system" not in path.parts
            and path.name != "agent_orchestra_stop_hook.sh"
        }

        self.assertLessEqual(required, actual)

    def test_launch_install_copies_all_minimal_runtime_python_modules(self) -> None:
        from agent_orchestra_minimal.launch_io import RUNTIME_FILES

        runtime_modules = {
            path.name
            for path in (CODEX / "agent_orchestra_minimal").glob("*.py")
            if path.name != "__init__.py"
        }

        self.assertLessEqual(runtime_modules, set(RUNTIME_FILES))

    def test_legacy_shell_stop_hook_is_not_part_of_minimal_runtime_contract(self) -> None:
        legacy_hook = CODEX / "hooks" / "agent_orchestra_stop_hook.sh"

        self.assertFalse(legacy_hook.exists(), "legacy shell Stop Hook should stay removed")

    def test_codex_o_is_only_a_thin_python_cli_shim(self) -> None:
        shim = (CODEX / "bin" / "codex-o").read_text(encoding="utf-8")

        self.assertIn("cli.py\" start", shim)
        self.assertNotIn("mktemp", shim)
        self.assertNotIn("cat >", shim)
        self.assertNotIn("tmux send-keys", shim)

    def test_runtime_code_has_no_polling_supervisor_or_spawn_dispatcher(self) -> None:
        forbidden = ("spawn_request", "dispatcher", "polling", "semantic mesh")
        for path in (CODEX / "agent_orchestra_minimal").glob("*.py"):
            if path.name == "__init__.py":
                continue
            text = path.read_text(encoding="utf-8").lower()
            for phrase in forbidden:
                with self.subTest(path=path.name, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_launch_skill_documents_codex_option_based_launch(self) -> None:
        text = (CODEX / "skills" / "agent-orchestra-launch" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(text.split())

        self.assertIn("generated `workspace/AGENTS.md` is the Agent behavior surface", normalized)
        self.assertIn("Layer `INSTRUCTIONS.md` files are specialist perspectives only", normalized)
        self.assertIn("--profile agent-orchestra", text)
        self.assertIn("--ask-for-approval never", text)
        self.assertIn("--sandbox workspace-write", text)
        self.assertIn("--enable hooks", text)
        self.assertIn("--cd", text)
        self.assertIn("--add-dir", text)
        self.assertIn("Do not create wrapper scripts", text)
        self.assertIn("codex exec", text)

    def test_agent_behavior_lives_in_agent_templates_not_runtime_python(self) -> None:
        common = (CODEX / "agent_orchestra_minimal" / "agent_templates" / "common.AGENTS.md").read_text(encoding="utf-8")
        common_normalized = " ".join(common.split())
        main = (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md").read_text(encoding="utf-8")
        professional = (
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md"
        ).read_text(encoding="utf-8")
        professional_normalized = " ".join(professional.split())
        runtime = (CODEX / "agent_orchestra_minimal" / "operating_identity.py").read_text(encoding="utf-8")
        team = (CODEX / "skills" / "agent-orchestra-team" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Layer `INSTRUCTIONS.md` files define specialist perspective only", common_normalized)
        self.assertIn("generated isolated `AGENTS.md` behavior と選択された layer perspective", common_normalized)
        self.assertNotIn("layer固有の観点で起動する", common)
        self.assertIn("You are the MainAgent", main)
        self.assertIn("AgentTeam steward", main)
        self.assertIn("You do not outrank ProfessionalAgents for editing", main)
        self.assertIn("Integration readiness is a Team decision", main)
        main_normalized = " ".join(main.split())
        self.assertIn("Do not ask ProfessionalAgents to run `pytest`", main_normalized)
        self.assertIn("do not run `pytest` yourself", main_normalized)
        self.assertIn("標準Pythonテストランナーは `unittest`", common)
        self.assertIn("`python3 -m unittest discover -s tests`", common)
        self.assertIn("`pytest` は標準依存ではない", common)
        self.assertIn("初期化済み task file", common)
        self.assertIn("`[status] done` で開始する", common)
        self.assertIn("`[status] progress` に切り替える", common)
        self.assertIn("You are a ProfessionalAgent", professional)
        self.assertIn("not your superior", professional)
        self.assertIn("review peers, request changes", professional)
        self.assertIn("Treat peer consultation as review evidence", professional)
        self.assertIn("move or record your scoped task in the shared task file under `[InReview]`", professional_normalized)
        self.assertIn("Move your scoped task to `[Done]` only when the accepted disposition is known", professional_normalized)
        self.assertIn("do not use this task update to decide whole-run completion", professional_normalized)
        for phrase in (
            "When you run or recommend verification",
            "`python3 -m unittest discover -s tests`",
            "Do not run or request `pytest`",
        ):
            self.assertIn(phrase, professional_normalized)
        self.assertIn("## Verification", team)
        self.assertIn("`python3 -m unittest discover -s tests`", team)
        self.assertIn("Do not ask Agents to run `pytest`", team)
        self.assertNotIn("AgentTeamは必要に応じてtmuxを使用し相互に直接相談する", runtime)
        self.assertNotIn("Integration readiness is a Team decision", runtime)
        self.assertNotIn("not your superior", runtime)

    def test_all_python_code_files_stay_under_hard_300_line_limit(self) -> None:
        roots = (
            CODEX / "agent_orchestra_minimal",
            CODEX / "hooks",
            ROOT / "tests",
        )

        for root in roots:
            for path in root.rglob("*.py"):
                if path.name == "__init__.py":
                    continue
                with self.subTest(path=path.relative_to(ROOT)):
                    line_count = len(path.read_text(encoding="utf-8").splitlines())
                    self.assertLessEqual(line_count, 300)

    def test_runtime_modules_with_split_responsibilities_stay_below_soft_target(self) -> None:
        split_modules = (
            CODEX / "agent_orchestra_minimal" / "launch_io.py",
            CODEX / "agent_orchestra_minimal" / "launch_material.py",
            CODEX / "agent_orchestra_minimal" / "launch_startup.py",
        )

        for path in split_modules:
            with self.subTest(path=path.relative_to(ROOT)):
                line_count = len(path.read_text(encoding="utf-8").splitlines())
                self.assertLessEqual(line_count, 200)

if __name__ == "__main__":
    unittest.main()
