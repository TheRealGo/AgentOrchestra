from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HandoffReleaseEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        if not (ROOT / "Handoff.md").exists():
            self.skipTest("Handoff.md is internal-only and absent from this tree")

    def _handoff_section(self, start_marker: str, end_marker: str) -> str:
        handoff = (ROOT / "Handoff.md").read_text(encoding="utf-8")
        start = handoff.index(start_marker)
        end = handoff.index(end_marker)
        return " ".join(handoff[start:end].split())

    def test_current_sweep_records_live_agentteam_mirror_verification_evidence(
        self,
    ) -> None:
        section = self._handoff_section(
            "Latest AgentTeam sweep after the 2026-06-08 live SPEC mirror verification pass",
            "Latest implementation follow-up after the 2026-06-08 safe equals-form extra-arg sweep",
        )

        for phrase in (
            "MainAgent plus `pro-runtime-08`",
            "`pro-quality-15`",
            "Both ProfessionalAgent task deliveries were accepted",
            "runtime source and `AgentOrchestra/` mirror content were inspected",
            "no runtime patch was warranted by the evidence",
            "`python3 -m unittest discover -s tests` passed, 257 tests",
            "`python3 -m py_compile` over `.codex/agent_orchestra_minimal/*.py` passed",
            "no drift except ignored `__pycache__`",
            "`nix flake check --no-build path:$PWD` passed",
            "`nix build path:$PWD#checks.$system.source-contract --no-link` passed",
            "candidate-ledger disposition: integrated",
            "live SPEC mirror verification evidence candidate",
            "deterministic finalization blockers for this scoped sweep: none known",
            "blocking objections: none known",
        ):
            self.assertIn(phrase, section)

    def test_current_review_records_deferred_safe_equals_form_extra_arg_candidate(
        self,
    ) -> None:
        section = self._handoff_section(
            "Latest implementation follow-up after the 2026-06-08 safe equals-form extra-arg sweep",
            "Latest generated-copy checks after the 2026-06-08 PR finalization disposition contract guard",
        )

        for phrase in (
            "safe value options such as `--model=gpt-5.5`, `-m=gpt-5.5`, and `-c=model_reasoning_effort=high`",
            "This was not a safety hole",
            "in-scope runtime usability improvement candidate",
            "root `.codex/` was read-only",
            "follow-up implementation was applied in the writable root after E2E exit",
            "candidate-ledger disposition: integrated",
            "safe equals-form `codex_args` candidate",
            "`python3 -m unittest tests.test_launch_args tests.test_handoff_release_evidence` passed",
            "deterministic finalization blockers for this scoped follow-up: none known",
            "blocking objections: none known",
        ):
            self.assertIn(phrase, section)

    def test_current_release_evidence_records_team_sufficiency_and_retirement_disposition(
        self,
    ) -> None:
        section = self._handoff_section(
            "Latest generated-copy checks after the 2026-06-08 Codex feature parser absent-state guard",
            "Latest generated-copy checks after the 2026-06-08 Issue #7 E2E current-test evidence guard",
        )

        for phrase in (
            "ProfessionalAgent sufficiency/retirement disposition",
            "smallest sufficient team",
            "MainAgent plus one Layer16 runtime reviewer",
            "no additional ProfessionalAgent or SubAgent viewpoint was required",
            "Accepted-retirement evidence is not claimed",
            "until MainAgent accepts the result",
            "review evidence rather than a retired-pane record",
            "equals-form runtime boundary overrides",
            "`--profile=agent-orchestra`",
            "`--enable=prevent_idle_sleep`",
            "`--cd=...`",
            "`--add-dir=...`",
            "equals-form launch-boundary override guard candidate",
            "`.codex/agent_orchestra_minimal/launch_args.py`",
        ):
            self.assertIn(phrase, section)

    def test_historical_tmux_baseline_evidence_records_spec_traceability(self) -> None:
        section = self._handoff_section(
            "Latest generated-copy checks after the 2026-06-07 tmux delivery baseline guard",
            "Latest generated-copy checks after the 2026-06-07 QA/release evidence consistency pass",
        )

        for phrase in (
            "live AgentOrchestra E2E run found a second tmux delivery false-acceptance risk",
            "fresh pasted message disappeared back to a ready prompt",
            "capture identical to the baseline screen",
            "stale activity marker",
            "SPEC sections: tmux Communication",
            "Hook-Driven Re-kick",
            "Release Evidence And SPEC Traceability",
            "Completion Criteria",
            "MainAgent owned the runtime fix",
            "`runtime-pro` provided the blocking runtime objection",
            "`docs-pro` reviewed docs/contracts",
            "affected scope: `.codex/agent_orchestra_minimal/tmux_delivery.py`",
            "`tests/test_tmux_send_edge_cases.py`",
            "`Handoff.md`",
            "`tests/test_change_control_surface.py`",
            "`python3 -m unittest tests.test_tmux_send_edge_cases` passed, 13 tests",
            "`python3 -m unittest discover -s tests` passed, 244 tests",
            "`python3 -m py_compile .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py` passed",
            "`git diff --check` passed",
            "candidate-ledger disposition: integrated",
            "tmux delivery baseline false-acceptance candidate",
            "deterministic finalization blockers: none known",
            "blocking objections: none known",
        ):
            self.assertIn(phrase, section)

    def test_historical_tmux_confirmation_evidence_records_spec_traceability(self) -> None:
        section = self._handoff_section(
            "Latest generated-copy checks after the 2026-06-07 tmux delivery confirmation fix",
            "Latest generated-copy checks after the 2026-06-07 QA evidence refresh",
        )

        for phrase in (
            "live AgentOrchestra E2E run found a runtime delivery false-positive",
            "SPEC sections: tmux Communication",
            "Hook-Driven Re-kick",
            "Release Evidence And SPEC Traceability",
            "owner_dri/reviewers: MainAgent owned the runtime fix",
            "`pro-runtime-08` and `pro-qa-15` provided independent runtime and QA review evidence",
            "affected scope: `.codex/agent_orchestra_minimal/tmux_delivery.py`",
            "`tests/test_tmux_send_edge_cases.py`",
            "`python3 -m unittest discover -s tests` passed, 238 tests",
            "find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0",
            "xargs -0 python3 -m py_compile",
            "`git diff --check -- AgentOrchestra` passed",
            "candidate-ledger disposition: integrated",
            "tmux delivery false-positive candidate",
            "deterministic finalization blockers: none known",
            "blocking objections: none known",
        ):
            self.assertIn(phrase, section)

    def test_historical_qa_evidence_records_spec_traceability(self) -> None:
        section = self._handoff_section(
            "Latest generated-copy checks after the 2026-06-07 QA evidence refresh",
            "Latest generated-copy checks after the 2026-05-27 launch profile and release-skill boundary pass",
        )

        for phrase in (
            "SPEC sections: Release Evidence And SPEC Traceability",
            "Completion Criteria",
            "owner_dri/reviewers: `pro-qa-15` owned this evidence refresh",
            "affected scope: `Handoff.md` and `tests/test_change_control_surface.py`",
            "`python3 -m unittest discover -s tests` passed, 233 tests",
            "`python3 -m unittest discover -s tests` passed, 235 tests",
            "find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0",
            "xargs -0 python3 -m py_compile",
            "`git diff --check -- AgentOrchestra` passed",
            "candidate-ledger disposition: integrated",
            "Handoff verification-count drift candidate",
            "deterministic finalization blockers: none known",
            "blocking objections: none known",
        ):
            self.assertIn(phrase, section)

    def test_historical_launch_profile_evidence_records_spec_traceability(self) -> None:
        section = self._handoff_section(
            "Latest generated-copy checks after the 2026-05-27 launch profile and release-skill boundary pass",
            "Latest generated-copy checks after the 2026-05-27 tmux probe split",
        )

        for phrase in (
            "SPEC sections: Instruction Isolation",
            "Skills",
            "Release Evidence And SPEC Traceability",
            "owner_dri/reviewers: MainAgent coordinated this pass with",
            "`pro-runtime-16` and `pro-docs-25` ProfessionalAgent review panes",
            "affected scope: `.codex/agent_orchestra_minimal/launch_args.py`",
            ".codex/agent_orchestra_minimal/launch_io.py",
            ".codex/skills/agent-orchestra-launch/SKILL.md",
            "candidate-ledger disposition: integrated",
            "`--profile` launch contract",
            "private launch-material permissions",
            "release Skill boundary",
            "`python3 -m unittest discover -s tests` passed, 215 tests",
            "deterministic finalization blockers: none known",
            "blocking objections: none known",
        ):
            self.assertIn(phrase, section)


if __name__ == "__main__":
    unittest.main()
