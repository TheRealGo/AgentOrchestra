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

    def test_degraded_delivery_success_updates_state_and_records_candidate(self) -> None:
        surfaces = [
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            _read(CODEX / "skills" / "agent-orchestra-tmux-common" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md"),
            _read(ROOT / "SPEC.md"),
        ]

        for text in surfaces:
            self.assertIn("helper", text)
            self.assertIn("later bounded capture", text)
            self.assertIn("accepted", text)
            self.assertIn("state", text)
            self.assertIn("`working`", text)
            self.assertIn("delivery-defect", text)
        self.assertIn("Do not leave state as `ready`", surfaces[0])
        self.assertIn("do not wait indefinitely", surfaces[0])

    def test_degraded_final_report_delivery_is_gate_or_candidate_evidence(self) -> None:
        surfaces = [
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            _read(CODEX / "skills" / "agent-orchestra-tmux-common" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md"),
            _read(ROOT / "SPEC.md"),
        ]

        for text in surfaces:
            self.assertIn("ProfessionalAgent", text)
            self.assertIn("report", text)
            self.assertIn("multiple submit attempts", text)
            self.assertIn("Gates", text)
            self.assertIn("Candidates", text)
            self.assertIn("zero_issue_blocker", text)
            self.assertIn("zero-issue", text)

    def test_live_delivery_retirement_and_self_exit_defects_need_later_clean_e2e(self) -> None:
        surfaces = [
            _read(CODEX / "skills" / "agent-orchestra-task-file" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-team" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"),
        ]

        for text in surfaces:
            self.assertIn("clean", text)
            self.assertIn("live E2E", text)
            self.assertIn("progress", text)
        for text in surfaces[:2]:
            self.assertIn("ProfessionalAgent retirement", text)
            self.assertIn("MainAgent self-exit", text)
            self.assertIn("completion-status", text)
            self.assertIn("focused unit regressions", text)
            self.assertIn("not enough", text)
            self.assertIn("zero-issue", text)
            self.assertIn("integrated", text)

    def test_selfe2e_self_exit_docs_include_auxiliary_shell_cleanup(self) -> None:
        surfaces = [
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            _read(CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md"),
            _read(CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"),
        ]

        for text in surfaces:
            self.assertIn("--allow-shell-cleanup-session-prefix AgentOrchestra-self-e2e-", text)
            self.assertIn("--cleanup-auxiliary-shells", text)
            self.assertIn("auxiliary_shell_panes", text)

    def test_phantom_background_terminal_is_bounded_candidate_not_indefinite_wait(self) -> None:
        surfaces = [
            _read(CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md"),
            _read(ROOT / "SPEC.md"),
        ]

        for text in surfaces:
            self.assertIn("background terminal", text)
            self.assertIn("declared timeout", text)
            self.assertIn("phantom or stuck background-terminal candidate", text)
            self.assertIn("equivalent scoped verification", text)
            self.assertIn("instead of waiting", text)

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

    def test_service_e2e_approval_cleanup_intake_is_specified_as_worker_path(self) -> None:
        spec = _read(ROOT / "SPEC.md")

        for phrase in (
            "ServiceE2E approval/UserNeeded/cleanup observations must enter the self-improvement worker path",
            "agent-orchestra service-e2e-intake",
            "expands the observations into Backlog, Acceptance, Gates, and Candidates",
            "replays the nine approval/UserNeeded/cleanup examples",
            "same autonomy and UserNeeded policy boundary used for worker decisions",
            "zero-issue completion is invalid",
        ):
            self.assertIn(phrase, spec)


if __name__ == "__main__":
    unittest.main()
