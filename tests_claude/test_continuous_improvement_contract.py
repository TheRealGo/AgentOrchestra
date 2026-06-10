from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ContinuousImprovementContractTests(unittest.TestCase):
    def test_spec_requires_next_cycle_for_known_in_scope_improvements(self) -> None:
        # The continuous-improvement organizational model lives in the shared,
        # runtime-neutral SPEC.md, which SPEC.claude.md declares "unchanged and
        # authoritative". Only the Claude launch delta moves to SPEC.claude.md.
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
            (ROOT / ".claude" / "skills" / "agent-orchestra-team" / "SKILL.md")
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
            (ROOT / ".claude" / "skills" / "agent-orchestra-team" / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        main_template = " ".join(
            (
                ROOT
                / ".claude"
                / "agent_orchestra_minimal"
                / "agent_templates"
                / "main.CLAUDE.md"
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
            "Use Claude Code subagents (the Task/Agent tool, `.claude/agents`) proactively",
            "normally use at least one SubAgent for critique, evidence review, or alternative analysis before final completion",
            "record the sufficiency rationale",
        ):
            self.assertIn(phrase, main_template)

    def test_guidance_recovers_from_malformed_candidate_rekick_loop(self) -> None:
        # The Stop Hook wake payload is a fixed, reasonless signal shared
        # byte-for-byte with Codex; a near-miss candidate disposition therefore
        # stays "unresolved" and re-kicks forever while the woken agent keeps
        # reporting "no open work". The shared deterministic core is left
        # identical to Codex (no divergence); convergence is recovered through
        # the Claude agent-facing guidance layer (skill + startup templates),
        # which is runtime-specific by design. This test pins that guidance.
        templates = ROOT / ".claude" / "agent_orchestra_minimal" / "agent_templates"

        task_file_skill = " ".join(
            (ROOT / ".claude" / "skills" / "agent-orchestra-task-file" / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for phrase in (
            "The Hook wake carries no reason, so a malformed candidate can re-kick forever",
            "Correct the line to the exact `candidate-id: disposition=<completed>; summary=...; evidence=...` shape",
            "makes the wake repeat without converging",
        ):
            self.assertIn(phrase, task_file_skill)

        main_template = " ".join(
            (templates / "main.CLAUDE.md").read_text(encoding="utf-8").split()
        )
        for phrase in (
            "A Hook wake carries no reason.",
            "the blocker is almost certainly an unresolved `[Candidates]` entry",
            "makes the Hook wake repeat without converging",
        ):
            self.assertIn(phrase, main_template)

        common_template = " ".join(
            (templates / "common.CLAUDE.md").read_text(encoding="utf-8").split()
        )
        for phrase in (
            "固定wakeは理由を含まない",
            "「open workなし」と報告して止まるだけだと状態が変わらず固定wakeが収束しない",
        ):
            self.assertIn(phrase, common_template)


if __name__ == "__main__":
    unittest.main()
