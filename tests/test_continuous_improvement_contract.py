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


if __name__ == "__main__":
    unittest.main()
