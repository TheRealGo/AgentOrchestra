from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ChangeControlSurfaceTests(unittest.TestCase):
    def test_github_actions_runs_source_contract_and_diff_check(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "agent-orchestra-source-contract.yml"
        ).read_text(encoding="utf-8")

        for phrase in (
            "git diff --check",
            "nix flake check --no-build",
            "nix build .#checks.x86_64-linux.source-contract",
            ".codex/agent_orchestra_minimal/**",
            ".codex/bin/**",
            "tests/**",
            ".github/pull_request_template.md",
        ):
            self.assertIn(phrase, workflow)

    def test_pr_template_requires_spec_e2e_update_for_runtime_changes(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("nix build .#checks.x86_64-linux.source-contract", template)
        self.assertIn("`SPEC.md` and runtime evidence are updated", template)
        self.assertIn("ProfessionalAgent sufficiency is recorded", template)
        self.assertIn("Shared task file finalization evidence is recorded", template)
        self.assertIn("ProfessionalAgent retirement evidence is recorded", template)
        self.assertIn("unresolved live tmux/Codex E2E gap", template)


if __name__ == "__main__":
    unittest.main()
