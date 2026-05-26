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
            "permissions:",
            "contents: read",
            "git diff --check",
            "find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0",
            "xargs -0 python3 -m py_compile",
            "python3 -m unittest discover -s tests",
            "nix flake check --no-build",
            "nix build .#checks.x86_64-linux.source-contract",
            "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4",
            "Checkout public release repository",
            "Checkout public release mirror",
            "startsWith(github.head_ref, 'version-')",
            'release_tag="v${release_version}"',
            "https://install.determinate.systems/nix",
            "sh -s -- install --no-confirm",
            ".codex/agent_orchestra_minimal/**",
            ".codex/bin/**",
            ".codex/hooks/**",
            ".codex/skills/agent-orchestra-*/**",
            "tests/**",
            "layers/**",
            "Handoff.md",
            ".gitignore",
            "flake.nix",
            "flake.lock",
            ".github/pull_request_template.md",
            ".github/workflows/agent-orchestra-source-contract.yml",
        ):
            self.assertIn(phrase, workflow)
        self.assertIn("git diff --check -- .codex tests layers Handoff.md SPEC.md .gitignore flake.nix", workflow)
        self.assertNotIn("E2E.md", workflow)

    def test_pr_template_requires_spec_e2e_update_for_runtime_changes(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("nix build .#checks.x86_64-linux.source-contract", template)
        self.assertIn("path-form Nix checks pass", template)
        self.assertIn("nix flake check --no-build path:$PWD", template)
        self.assertIn("nix build path:$PWD#checks.$system.source-contract", template)
        self.assertIn("`python3 -m py_compile` passes", template)
        self.assertIn("`git diff --check -- .codex tests layers Handoff.md SPEC.md .gitignore flake.nix", template)
        self.assertNotIn("E2E.md", template)
        self.assertIn("`SPEC.md` and runtime evidence are updated", template)
        self.assertIn("Change-unit evidence is recorded", template)
        self.assertIn("owner_dri", template)
        self.assertIn("affected scope, reviewers, peer consultation disposition when applicable", template)
        self.assertIn("blocking objections, and resolution/evidence", template)
        self.assertIn("ProfessionalAgent sufficiency is recorded", template)
        self.assertIn("Final improvement-candidate sweep evidence is recorded", template)
        self.assertIn("ProfessionalAgent recommendations, skipped verification", template)
        self.assertIn("Shared task file finalization evidence is recorded", template)
        self.assertIn("every `[Candidates]` item has a completed disposition", template)
        self.assertIn("deterministic finalization blocker list is empty", template)
        self.assertIn("SPEC traceability is recorded", template)
        self.assertIn("affected SPEC section", template)
        self.assertIn("candidate-ledger disposition", template)
        self.assertIn("ProfessionalAgent retirement evidence is recorded", template)
        self.assertIn("unresolved live tmux/Codex E2E gap", template)

    def test_handoff_matches_stop_hook_pane_fallback_contract(self) -> None:
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")

        self.assertIn("invalid explicit pane env never falls back", handoff)
        self.assertIn("missing or invalid own pane env can wake", handoff)
        self.assertNotIn("invalid own pane env\n    still takes no action", handoff)

    def test_handoff_current_verification_names_latest_check_result_first(self) -> None:
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")

        latest_index = handoff.index("Latest generated-copy checks after the 2026-05-26 live AgentTeam review")
        earlier_index = handoff.index("Latest generated-copy checks after the 2026-05-26 SPEC-driven refresh")
        handoff_normalized = " ".join(handoff.split())

        self.assertLess(latest_index, earlier_index)
        self.assertIn("passed, 194 tests after adding the false-negative regression", handoff_normalized)
        self.assertNotIn("Latest root checks after accepting the current generated-copy proposal", handoff)

    def test_handoff_separates_residual_checks_from_historical_followup_evidence(self) -> None:
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")

        remaining_index = handoff.index("## Remaining Operational Checks")
        historical_index = handoff.index("## Historical Follow-up Evidence")
        liveness_index = handoff.index("2026-05-25 follow-up liveness pass")
        wording_index = handoff.index("2026-05-25 generated-startup wording pass")

        self.assertLess(remaining_index, historical_index)
        self.assertLess(historical_index, liveness_index)
        self.assertLess(historical_index, wording_index)

    def test_handoff_latest_release_evidence_records_spec_traceability(self) -> None:
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")
        latest_start = handoff.index("Latest generated-copy checks after the 2026-05-26 live AgentTeam review")
        earlier_start = handoff.index("Latest generated-copy checks after the 2026-05-26 SPEC-driven refresh")
        latest_section = handoff[latest_start:earlier_start]
        latest_normalized = " ".join(latest_section.split())

        for phrase in (
            "SPEC sections: Team Execution Sufficiency",
            "Release Evidence And SPEC Traceability",
            "owner_dri/reviewers: MainAgent owned the release-evidence refresh",
            "`pro-backend-runtime` reviewed runtime Python/test consistency",
            "`pro-docs-spec` reviewed SPEC/docs/skill/test-contract consistency",
            "affected scope: `Handoff.md`, `tests/test_change_control_surface.py`",
            "candidate-ledger disposition: integrated",
            "live tmux delivery false-negative candidate",
            "tests/test_tmux_send_edge_cases.py",
            "blocking objections: none",
            "ProfessionalAgent panes `%1332` / `%1333`",
        ):
            self.assertIn(phrase, latest_normalized)


if __name__ == "__main__":
    unittest.main()
