from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"


class CompletionProfileContractTests(unittest.TestCase):
    def test_local_first_gates_stay_separate_from_public_release(self) -> None:
        surfaces = [
            ROOT / "SPEC.md",
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md",
            CODEX / "skills" / "agent-orchestra-team" / "SKILL.md",
        ]

        for path in surfaces:
            normalized = " ".join(path.read_text(encoding="utf-8").split())
            self.assertIn("local_two_user_production_like", normalized, path)
            self.assertIn("public_release", normalized, path)
            self.assertIn("local Safari", normalized, path)
            self.assertIn("iPhone Safari", normalized, path)
            self.assertIn("direct local install", normalized, path)
            self.assertIn("persistence", normalized, path)
            self.assertIn("production-compatible architecture", normalized, path)
            self.assertIn("public store", normalized, path)
            self.assertIn("production provider", normalized, path)
            self.assertIn("deferred or out-of-scope", normalized, path)


if __name__ == "__main__":
    unittest.main()
