from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ChangeControlSurfaceTests(unittest.TestCase):
    def test_github_actions_runs_claude_source_contract_and_diff_check(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "agent-orchestra-claude-contract.yml"
        ).read_text(encoding="utf-8")

        for phrase in (
            "name: agent-orchestra claude contract",
            "permissions:",
            "contents: read",
            "git diff --check -- .claude tests_claude layers SPEC.claude.md .gitignore flake.nix flake.lock .github",
            "find .claude/agent_orchestra_minimal .claude/hooks tests_claude -name '*.py' -print0",
            "xargs -0 python3 -m py_compile",
            "python3 -m unittest discover -s tests_claude",
            "nix flake check --no-build",
            "nix build .#checks.x86_64-linux.claude-source-contract",
            "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4",
            "https://install.determinate.systems/nix",
            "sh -s -- install --no-confirm",
            ".claude/agent_orchestra_minimal/**",
            ".claude/bin/**",
            ".claude/hooks/**",
            ".claude/skills/agent-orchestra-*/**",
            "tests_claude/**",
            "SPEC.claude.md",
            "layers/**",
            ".gitignore",
            "flake.nix",
            "flake.lock",
            ".github/workflows/agent-orchestra-claude-contract.yml",
        ):
            self.assertIn(phrase, workflow)

        # This workflow is the Claude contract surface; it must not check the
        # Codex tree or the Codex `source-contract` derivation.
        self.assertNotIn(".codex", workflow)
        self.assertNotIn("agent-orchestra-source-contract.yml", workflow)

    def test_codex_source_contract_workflow_still_coexists(self) -> None:
        # The Codex change-control workflow is unchanged and continues to exist
        # alongside the Claude one (両対応, no regression).
        codex_workflow = ROOT / ".github" / "workflows" / "agent-orchestra-source-contract.yml"
        self.assertTrue(codex_workflow.is_file())
        text = codex_workflow.read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover -s tests", text)


if __name__ == "__main__":
    unittest.main()
