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
            "nix flake check --no-build path:$PWD",
            "nix build path:$PWD#checks.x86_64-linux.source-contract",
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
            "E2E.md",
            "README.md",
            "README.ja.md",
            ".gitignore",
            "flake.nix",
            "flake.lock",
            ".github/pull_request_template.md",
            ".github/workflows/agent-orchestra-source-contract.yml",
        ):
            self.assertIn(phrase, workflow)
        self.assertIn(
            "git diff --check -- .codex tests layers Handoff.md E2E.md README.md README.ja.md SPEC.md .gitignore flake.nix",
            workflow,
        )
        self.assertNotIn("pytest", workflow)

    def test_pr_template_requires_spec_e2e_update_for_runtime_changes(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("nix build .#checks.x86_64-linux.source-contract", template)
        self.assertIn("path-form Nix checks pass", template)
        self.assertIn("nix flake check --no-build path:$PWD", template)
        self.assertIn("nix build path:$PWD#checks.$system.source-contract", template)
        self.assertIn("standard Python runner remains `unittest`", template)
        self.assertIn("`pytest` is not substituted", template)
        self.assertIn("`python3 -m py_compile` passes", template)
        self.assertIn("runtime, instruction, evidence, or contributor-doc changes", template)
        self.assertIn("`git diff --check -- .codex tests layers Handoff.md E2E.md README.md README.ja.md SPEC.md .gitignore flake.nix", template)
        self.assertIn("`SPEC.md` and runtime evidence are updated", template)
        self.assertIn("Change-unit evidence is recorded", template)
        self.assertIn("owner_dri", template)
        self.assertIn("affected scope, reviewers, peer consultation disposition when applicable", template)
        self.assertIn("blocking objections, and resolution/evidence", template)
        self.assertIn("ProfessionalAgent sufficiency is recorded", template)
        self.assertIn("Final improvement-candidate sweep evidence is recorded", template)
        self.assertIn("ProfessionalAgent recommendations, skipped verification", template)
        for disposition in (
            "integrated",
            "rejected",
            "deferred",
            "blocked",
            "out-of-scope",
            "`needs_user`",
            "[Backlog]",
        ):
            self.assertIn(disposition, template)
        self.assertIn("Shared task file finalization evidence is recorded", template)
        self.assertIn("every `[Candidates]` item has a completed disposition", template)
        self.assertIn("deterministic finalization blocker list is empty", template)
        self.assertIn("SPEC traceability is recorded", template)
        self.assertIn("affected SPEC section", template)
        self.assertIn("candidate-ledger disposition", template)
        self.assertIn("ProfessionalAgent retirement evidence is recorded", template)
        self.assertIn("unresolved live tmux/Codex E2E gap", template)

    def test_handoff_matches_stop_hook_pane_fallback_contract(self) -> None:
        if not (ROOT / "Handoff.md").exists():
            self.skipTest("Handoff.md is internal-only and absent from this tree")
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")

        self.assertIn("invalid explicit pane env never falls back", handoff)
        self.assertIn("missing or invalid own pane env can wake", handoff)
        self.assertNotIn("invalid own pane env\n    still takes no action", handoff)

    def test_handoff_current_verification_names_latest_check_result_first(self) -> None:
        if not (ROOT / "Handoff.md").exists():
            self.skipTest("Handoff.md is internal-only and absent from this tree")
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")

        pr_disposition_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 PR finalization disposition contract guard"
        )
        task_file_doctor_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 task-file doctor finalization guard"
        )
        e2e_gate_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 E2E evidence CI gate guard"
        )
        feature_parser_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 Codex feature parser absent-state guard"
        )
        issue7_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 Issue #7 E2E current-test evidence guard"
        )
        readme_contract_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 README verification contract guard"
        )
        path_form_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 path-form README evidence guard"
        )
        prevent_idle_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 prevent-idle-sleep launch guard"
        )
        runner_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 unittest runner guard"
        )
        current_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-08 SPEC alignment sweep"
        )
        latest_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-07 tmux delivery baseline guard"
        )
        release_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-07 QA/release evidence consistency pass"
        )
        tmux_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-07 tmux delivery confirmation fix"
        )
        qa_index = handoff.index(
            "Latest generated-copy checks after the 2026-06-07 QA evidence refresh"
        )
        previous_index = handoff.index(
            "Latest generated-copy checks after the 2026-05-27 launch profile and release-skill boundary pass"
        )
        earlier_index = handoff.index("Latest generated-copy checks after the 2026-05-27 README docs gate")
        handoff_normalized = " ".join(handoff.split())

        ordered_indexes = (
            pr_disposition_index,
            task_file_doctor_index,
            e2e_gate_index,
            feature_parser_index,
            issue7_index,
            readme_contract_index,
            path_form_index,
            prevent_idle_index,
            runner_index,
            current_index,
            latest_index,
            release_index,
            tmux_index,
            qa_index,
            previous_index,
            earlier_index,
        )
        for left, right in zip(ordered_indexes, ordered_indexes[1:]):
            self.assertLess(left, right)
        for phrase in (
            "PR finalization disposition contract guard",
            "executable change-control test did not assert the terminal disposition vocabulary",
            "Change-unit evidence is recorded",
            "PR finalization disposition contract candidate",
            "task-file doctor finalization guard",
            "could not directly report deterministic task-file finalization blockers",
            "`doctor --task-file`",
            "task-file doctor finalization guard candidate",
            "E2E evidence CI gate guard",
            "source-contract workflow path filters and whitespace check excluded `E2E.md`",
            "evidence-only E2E updates bypass the CI/release evidence gate",
            "E2E evidence CI gate candidate",
            "Codex feature parser absent-state guard",
            "could be parsed as `present`",
            "feature parser absent-state guard candidate",
            "Issue #7 E2E current-test evidence guard",
            "removed Issue #7 acceptance modules",
            "tests/test_continuous_improvement_contract.py",
            "Issue #7 E2E current-test evidence guard candidate",
            "README verification contract guard",
            "path-form Nix line wrapping",
            "not delivered because the peer pane remained busy",
            "README verification contract guard candidate",
            "path-form README evidence guard",
            "README contributor verification only showed repository-root Nix commands",
            "path-form README evidence candidate",
            "prevent-idle-sleep launch guard",
            "automatic Codex `prevent_idle_sleep` launch behavior",
            "release-evidence freshness candidate",
            "`.codex/agent_orchestra_minimal/codex_features.py`",
            "unittest runner guard",
            "`pytest`, which is not a project dependency",
            "passed, 245 tests",
            "SPEC alignment sweep",
            "tmux peer-prompt guard candidate",
            "`unittest` release-evidence guard candidate",
            "path-form `nix flake check",
            "passed, 244 tests",
            "tmux delivery baseline guard",
            "QA/release evidence consistency pass",
            "tmux delivery confirmation fix",
            "QA evidence refresh",
        ):
            self.assertIn(phrase, handoff_normalized)
        self.assertNotIn("Latest root checks after accepting the current generated-copy proposal", handoff)

    def test_handoff_separates_residual_checks_from_historical_followup_evidence(self) -> None:
        if not (ROOT / "Handoff.md").exists():
            self.skipTest("Handoff.md is internal-only and absent from this tree")
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")

        remaining_index = handoff.index("## Remaining Operational Checks")
        historical_index = handoff.index("## Historical Follow-up Evidence")
        liveness_index = handoff.index("2026-05-25 follow-up liveness pass")
        wording_index = handoff.index("2026-05-25 generated-startup wording pass")

        self.assertLess(remaining_index, historical_index)
        self.assertLess(historical_index, liveness_index)
        self.assertLess(historical_index, wording_index)


if __name__ == "__main__":
    unittest.main()
