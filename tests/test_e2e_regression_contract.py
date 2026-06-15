from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"


def _read(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class E2ERegressionContractTests(unittest.TestCase):
    def test_doc_discovery_is_case_insensitive(self) -> None:
        surfaces = {
            "main": _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            "team": _read(CODEX / "skills" / "agent-orchestra-team" / "SKILL.md"),
            "spec": _read(ROOT / "SPEC.md"),
            "readme": _read(ROOT / "README.md"),
        }

        for text in surfaces.values():
            self.assertIn("case-insensitive", text)
            self.assertIn("Spec.md", text)
            self.assertIn("UI.md", text)

    def test_professional_assignments_are_not_left_at_default_composer(self) -> None:
        for text in (
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            _read(CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md"),
        ):
            self.assertIn("immediately", text)
            self.assertIn("default composer", text)
            self.assertIn("`[Candidates]` issue", text)
            self.assertIn("A non-zero `agent_orchestra_minimal.tmux_send` result", text)
            self.assertIn("blocking delivery defect", text)
            self.assertIn("Do not mark that ProfessionalAgent as working", text)

    def test_visual_routes_have_outer_timeout_and_no_unbounded_retry(self) -> None:
        professional = _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md")
        surfaces = [
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            professional,
            _read(CODEX / "skills" / "agent-orchestra-team" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md"),
            _read(ROOT / "SPEC.md"),
            _read(ROOT / "README.md"),
        ]

        for text in surfaces:
            self.assertIn("outer wall-clock timeout", text)
            self.assertIn("unbounded browser run", text)
        for text in (
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            _read(CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md"),
        ):
            self.assertIn("first `MachPortRendezvous`", text)
            self.assertIn("switch to another concrete evidence route", text)

    def test_task_file_updates_reread_and_merge_latest_state(self) -> None:
        task_file_skill = _read(CODEX / "skills" / "agent-orchestra-task-file" / "SKILL.md")

        self.assertIn("Before every write, re-read the current shared task file", task_file_skill)
        self.assertIn("task-file merge race", task_file_skill)

    def test_operational_e2e_defects_are_not_integrated_by_workaround(self) -> None:
        surfaces = [
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            _read(CODEX / "skills" / "agent-orchestra-team" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-task-file" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md"),
        ]

        for text in surfaces:
            self.assertIn("MCP", text)
            self.assertIn("workaround", text)
            self.assertIn("integrated", text)
        self.assertIn("later E2E run proves", surfaces[1])


if __name__ == "__main__":
    unittest.main()
