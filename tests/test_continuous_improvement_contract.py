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
            "After every `runtime_wake` and at the start of every improvement cycle",
            "resynchronize from the generated startup `AGENTS.md`, this MainAgent Role Contract",
            "Treat the wake payload as a pointer back to already-loaded operating contracts",
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

    def test_e2e_names_issue7_acceptance_gate(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        for phrase in (
            "Issue #7",
            "Long-Run Memory Dilution",
            "`runtime_wake`",
            "bounded resync signal",
            "improvement-cycle boundary",
            "cycle_done",
            "generated startup `AGENTS.md`",
            "MainAgent Role Contract",
            "`agent-orchestra-team` Skill",
            "shared task file",
            "Agent state",
            "smallest sufficient team",
            "Layer15 process/QA",
            "Team review",
            "blocking-objection",
            "candidate disposition",
            "ProfessionalAgent retirement audit",
            "accepted ProfessionalAgents are marked `retired`",
            "sent `/exit`, and have pane cleanup verified",
            "`kill-pane` only as cleanup after the attempted `/exit`",
            "required checks run, skipped, or deferred with reason",
            "python3 -m unittest discover -s tests",
            "python3 -m py_compile",
            "git diff --check",
            "live long-duration execution",
            "long-run-equivalent contract check",
            "Residual risk remains",
        ):
            self.assertIn(phrase, spec)

    def test_spec_fixed_wake_payload_matches_runtime_resync_contract(self) -> None:
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        canonical_payload = """\
Canonical payload:

```text
runtime_wake
source=hook
user_instruction=false
resync=startup_agents_role_contract_team_skill_task_state
action=resume_existing_work_after_resync
```"""

        for phrase in (
            "runtime_wake",
            "source=hook",
            "user_instruction=false",
            "resync=startup_agents_role_contract_team_skill_task_state",
            "action=resume_existing_work_after_resync",
        ):
            self.assertIn(phrase, spec)
        self.assertIn(canonical_payload, spec)
        self.assertIn("bounded resync signal", spec)

    def test_spec_documents_issue7_long_run_resync_acceptance(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        for phrase in (
            "Long-Run Memory Dilution",
            "120-hour-class runs",
            "every `runtime_wake` and every improvement-cycle boundary",
            "generated startup `AGENTS.md`",
            "MainAgent Role Contract",
            "`agent-orchestra-team` Skill",
            "shared task file",
            "Agent state",
            "ProfessionalAgent launch judgment",
            "Layer15 process/QA",
            "Team review and blocking-objection handling",
            "ProfessionalAgent retirement audit",
            "Residual risk remains",
        ):
            self.assertIn(phrase, spec)

    def test_completion_criteria_include_long_run_equivalent_cycle_check(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        for phrase in (
            "long-run-equivalent wake/cycle repetition",
            "MainAgent resync",
            "ProfessionalAgent launch",
            "Layer15 process/QA judgment",
            "Team review",
            "final candidate sweep",
            "pane-retirement audit",
        ):
            self.assertIn(phrase, spec)

    def test_readmes_summarize_completion_state_contract(self) -> None:
        readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
        readme_ja = " ".join((ROOT / "README.ja.md").read_text(encoding="utf-8").split())

        for phrase in (
            "The shared task file starts at `[status] done` only as the empty quiet baseline",
            "`[status] progress`",
            "every `[Candidates]` ledger item has an id, summary, completed disposition, and evidence pointer",
            "Accepted ProfessionalAgents are marked `retired`, sent `/exit`",
            "AGENT_ORCHESTRA_TARGET_PROJECT",
            "AGENT_ORCHESTRA_EDIT_ROOT",
        ):
            self.assertIn(phrase, readme)
        for phrase in (
            "共有タスクファイルの `[status] done`",
            "`[status] progress`",
            "`[Candidates]` ledger",
            "id、summary、完了 disposition、evidence pointer",
            "ProfessionalAgent は `retired` にし",
            "AGENT_ORCHESTRA_TARGET_PROJECT",
            "AGENT_ORCHESTRA_EDIT_ROOT",
        ):
            self.assertIn(phrase, readme_ja)


if __name__ == "__main__":
    unittest.main()
