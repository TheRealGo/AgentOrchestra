from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"


class LongVerificationContractTests(unittest.TestCase):
    def test_long_external_verification_must_be_bounded(self) -> None:
        main_template = " ".join(
            (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md")
            .read_text(encoding="utf-8")
            .split()
        )
        team_skill = " ".join(
            (CODEX / "skills" / "agent-orchestra-team" / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        env_skill = " ".join(
            (CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        for surface in (main_template, team_skill, env_skill, spec):
            for phrase in (
                "Nix builds",
                "timeout",
                "waiting indefinitely",
                "`[Gates]` or `[Candidates]`",
                "equivalent",
            ):
                self.assertIn(phrase, surface)


if __name__ == "__main__":
    unittest.main()
