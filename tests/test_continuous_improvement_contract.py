from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ContinuousImprovementContractTests(unittest.TestCase):
    def test_spec_requires_next_cycle_for_known_in_scope_improvements(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        for phrase in (
            "For continuous self-improvement goals",
            "another cycle is required before writing `[status] done`",
            "every known in-scope improvement candidate has been integrated",
            "put it in `[Backlog]` and keep `[status] = progress`",
            "not merely that the current patch was accepted",
            "ProfessionalAgent recommendations",
            "failed or skipped verification gaps",
            "E2E observations",
            "operational issues discovered during the run",
            "must not hide these as narrative-only notes",
            "final improvement-candidate sweep",
            "create the next-cycle Backlog item",
        ):
            self.assertIn(phrase, spec)

    def test_team_skill_requires_final_improvement_candidate_sweep(self) -> None:
        skill = " ".join(
            (ROOT / ".codex" / "skills" / "agent-orchestra-team" / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )

        for phrase in (
            "final improvement-candidate sweep",
            "every known in-scope improvement candidate",
            "add it to `[Backlog]`, keep `[status] = progress`, and start the next cycle",
            "Do not treat `cycle_done` or accepted current patches as full completion",
        ):
            self.assertIn(phrase, skill)

    def test_team_skill_and_main_template_require_subagent_opportunity_check(self) -> None:
        skill = " ".join(
            (ROOT / ".codex" / "skills" / "agent-orchestra-team" / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        main_template = " ".join(
            (
                ROOT
                / ".codex"
                / "agent_orchestra_minimal"
                / "agent_templates"
                / "main.AGENTS.md"
            )
            .read_text(encoding="utf-8")
            .split()
        )

        for phrase in (
            "perform a SubAgent opportunity check before final review",
            "record why the owning Agent's context and evidence are sufficient",
        ):
            self.assertIn(phrase, skill)
        for phrase in (
            "Use Codex-native SubAgents proactively",
            "normally use at least one SubAgent for critique, evidence review, or alternative analysis before final completion",
            "record the sufficiency rationale",
        ):
            self.assertIn(phrase, main_template)

    def test_professional_template_keeps_ready_work_in_review_until_accepted(
        self,
    ) -> None:
        professional_template = " ".join(
            (
                ROOT
                / ".codex"
                / "agent_orchestra_minimal"
                / "agent_templates"
                / "professional.AGENTS.md"
            )
            .read_text(encoding="utf-8")
            .split()
        )

        for phrase in (
            "set your Agent state to `ready_for_review`",
            "scoped task in the shared task file under `[InReview]`",
            "Move your scoped task to `[Done]` only when the accepted disposition is known",
            "do not use this task update to decide whole-run completion",
        ):
            self.assertIn(phrase, professional_template)

    def test_spec_keeps_professional_ready_work_in_review_until_accepted(
        self,
    ) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        for phrase in (
            "records `ready_for_review` before or as it reports",
            "records the scoped task in `[InReview]` rather than `[Done]`",
            "until the accepted disposition is known",
        ):
            self.assertIn(phrase, spec)


if __name__ == "__main__":
    unittest.main()
