from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"


class E2ESkillBoundaryContractTests(unittest.TestCase):
    def test_service_e2e_skill_forbids_cao_remote_control(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-service-e2e-improvement" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "CAO is not a product co-pilot",
            "After the initial plan delivery, CAO records what AgentOrchestra does and does not do",
            "Repeated \"continue with P0/P1\", priority, handoff, or implementation-detail prompts are interventions",
            "Do not keep the run moving by repeatedly sending product task instructions",
            "Do not immediately switch to self-improvement E2E",
            "multiple MainAgent panes/windows for the same run or workspace",
            "duplicate `main`, `main-recovery`, stale, usage-limited, unsupported-model/400, or interrupted panes",
            "The service E2E exists to test whether AgentOrchestra completes the service autonomously",
            "CAO must not convert it into manual remote control",
            "CAO is mainly a recorder for AgentOrchestra improvement",
            "telling codex-o the next product subtask after every chunk",
            "asking for handoff or stopping the service E2E while codex-o is still actively pursuing the service goal",
            "using CAO approval/commands as the mechanism that lets low-risk work proceed",
            ".tmp/agent-orchestra-service-e2e/status",
            "launch material uses Codex `--ask-for-approval never`",
            "low-risk local browser/mobile/iOS verification reruns and run-scoped cleanup must not stop on CAO approval prompts",
            "CAO-driven recovery as proof that AgentOrchestra worked",
            "Do not feed service defects back as step-by-step prompts during a running service E2E",
            "Service-E2E-discovered AgentOrchestra defects are not closed merely because CAO worked around them",
            "Do not switch from service E2E to self-improvement E2E merely because CAO found an AgentOrchestra defect",
        ):
            self.assertIn(phrase, normalized)

    def test_service_e2e_skill_routes_approval_cleanup_observations_through_intake(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-service-e2e-improvement" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "When the observation includes approval/UserNeeded/cleanup or CAO-intervention cases",
            "agent-orchestra service-e2e-intake",
            "--brief-file /path/to/service-e2e-agent-orchestra-defects.md",
            "--task-file \"$AGENT_ORCHESTRA_RUN_DIR/tasks.ini\"",
            "expands the ServiceE2E worker observations into Backlog, Acceptance, Gates, and Candidates",
            "replays the nine approval/UserNeeded/cleanup classifications",
            "same autonomy and UserNeeded policy path used by the worker decision boundary",
            "do not claim a zero-issue ServiceE2E or SelfE2E result from doctor/tests alone",
        ):
            self.assertIn(phrase, normalized)

    def test_self_improvement_skill_initializes_nested_git_boundary(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "Initialize the generated copy as its own nested Git repository baseline",
            "git -C AgentOrchestra init",
            "git -C AgentOrchestra add -A",
            "self-improvement baseline",
            "git -C AgentOrchestra rev-parse --show-toplevel",
            "git -C AgentOrchestra status --short",
            "prevents `git status`, `git diff --check`, and ProfessionalAgent review commands inside the copy from walking up",
            "A self- improvement E2E is invalid",
            "resolves to the parent dev repo",
            "parent paths such as `../.codex/...`",
        ):
            self.assertIn(phrase, normalized)

    def test_self_improvement_skill_uses_copy_status_path_in_prompts(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        self.assertIn("prompt, watchdog, or handoff evidence", normalized)
        self.assertIn("`.tmp/self-improvement-e2e/status`", normalized)
        self.assertIn("not the older `.codex/tmp/improvement-cycle.status` helper path", normalized)
        self.assertIn("read the same file back", normalized)
        self.assertIn("observed content is exactly `done`", normalized)
        self.assertIn("use `/exit` only after zero-issue finalization and `[status] done`", normalized)
        self.assertIn("final orchestra action", normalized)
        self.assertNotIn("`/exit` before completion", normalized)

    def test_self_improvement_skill_accepts_service_e2e_defect_briefs(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "Service-E2E Defect Intake",
            "When a real-service E2E exposes AgentOrchestra autonomy defects",
            "Do not treat CAO workarounds as success",
            "The defect brief is input evidence, not a CAO-authored implementation script",
            "duplicate MainAgent windows or panes",
            "unsupported-model 400 panes",
            "usage-limit closure gaps",
            "composer residue",
            "CAO repeatedly sending product next-step prompts",
            "Do not turn the brief into detailed file-level orders",
            "improve AgentOrchestra so the same service E2E would need less CAO intervention",
        ):
            self.assertIn(phrase, normalized)

    def test_self_improvement_skill_keeps_cao_as_observer_until_apply_back(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "During the E2E run, CAO is primarily an observer and record keeper",
            "Do not steer MainAgent through implementation details",
            "record that as an AgentOrchestra autonomy defect",
            "The special CAO responsibility in self-improvement is apply-back after AgentOrchestra has produced candidate changes",
            "should not replace the self-improvement run with direct parent-repo implementation while the E2E is still in progress",
            "CAO will not provide routine next-step prompts",
            "AgentOrchestra must plan, execute, verify, recover from ordinary fixable stops",
            "If CAO intervened during the run, completion is not zero-issue",
            "the E2E only reached them because CAO manually drove the run",
        ):
            self.assertIn(phrase, normalized)

    def test_self_improvement_skill_requires_dedicated_tmux_session(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "Run the self-improvement worker in its own tmux session",
            "Never start `python3 .codex/agent_orchestra_minimal/cli.py start ...` directly inside the ToO CAO pane/session",
            "the final `/exit`/self-exit cleanup can close that CAO pane",
            "The ToO CAO pane stays alive as the supervisor",
            "dedicated session such as `AgentOrchestra-self-e2e-YYYYMMDD-HHMMSS`",
            "Create a fresh dedicated tmux session for the SelfE2E worker",
            'SELF_E2E_SESSION="AgentOrchestra-self-e2e-$(date +%Y%m%d-%H%M%S)"',
            "CAO supervisor pane",
            "SelfE2E worker pane",
            "The run is invalid if `SELF_E2E_PANE` is the ToO CAO pane",
            "if the session name is `ToO`, `CAO`, `cao`, or `ToO-codex-o`",
            "Paste this shell command only into the `SELF_E2E_PANE`, not the ToO CAO pane",
            "The `SelfE2E worker pane` is the pane that may receive `/exit`",
            "CAO supervisor pane must not receive `/exit`",
        ):
            self.assertIn(phrase, normalized)

    def test_self_improvement_skill_requires_dedicated_tmux_session_and_safe_self_exit(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "Self-improvement E2E must run in a dedicated tmux session or window",
            "Do not launch the self-improvement MainAgent directly inside an active ToO CAO pane/session",
            "self-exit cleanup contract applies only to the self-improvement MainAgent pane",
            "Self-exit cleanup must never target or kill the CAO pane, ToO pane, or any service-E2E controller pane",
            "keep status `progress` and record a SelfE2E session-boundary defect",
            "verify `/exit`/self-exit targets the self-improvement MainAgent pane",
            "--allow-shell-cleanup-session-prefix AgentOrchestra-self-e2e-",
            "recorded SelfE2E worker pane",
            "without touching CAO/ToO panes",
        ):
            self.assertIn(phrase, normalized)

    def test_self_improvement_skill_blocks_zero_issue_on_approval_or_degraded_delivery(self) -> None:
        skill = (
            CODEX / "skills" / "agent-orchestra-self-improvement-e2e" / "SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "CAO approval is needed for low-risk copy-local edits",
            "record it as an autonomy blocker",
            "unless a later regression run proves no CAO approval input was needed",
            "status-file readback is exactly `done`",
            "required final ProfessionalAgent report delivery with degraded retries",
            "keeps the run non-zero",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
