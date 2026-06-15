from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"


class CompletionQualityContractTests(unittest.TestCase):
    def test_main_template_requires_acceptance_spec_trace_and_visual_gate(self) -> None:
        template = (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(template.split())

        for phrase in (
            "Build an `[Acceptance]` ledger first",
            "write that initial `[Acceptance]` and `[Gates]` ledger to the shared task file before performing substantial implementation diff review",
            "Do not leave `[Acceptance]` and `[Gates]` empty while continuing into code audit",
            "`SPEC.md`, README files, referenced issues, and relevant design docs",
            "Resolve requirement documents case-insensitively",
            "use a case-insensitive file search such as `find ... -iname 'spec.md'`",
            "Conversation-level user clarifications are authoritative requirement sources",
            "Do not discard or downgrade a user clarification",
            "preserve the concrete requirement",
            "Layer 04 requirements, Layer 15 QA",
            "Layer 05/06 when UI or interaction design is involved",
            "For broad, open-ended, product-building, or live E2E validation tasks",
            "The absence of already-active ProfessionalAgent panes is not a sufficiency rationale",
            "derive the primary verification environment from the product's documented or implemented use case",
            "Do not add desktop, mobile, responsive, or other platform coverage as a completion requirement unless",
            "Treat useful but out-of-scope device coverage as a deferred improvement candidate",
            "\"Playwright MCP is unavailable\" is not an excuse",
            "unstarted required environment",
            "missing required MCP/tool evidence",
            "every `[Gates]` item is passed",
            "Missing or broken environment pieces are not a stopping condition by themselves",
            "repository-native setup, an existing Docker compose path",
            "Keep `[status] progress` while any autonomous route remains",
            "exact external credential, approval, network access, service, hardware, or scope change",
            "Do not delete untracked files",
            "`result`/`result-*` symlinks",
            "Do not delete `AGENT_ORCHESTRA_RUN_DIR` itself",
            "Only remove specific disposable resources you created for the current run",
            "server manifest path, `base_url`, port,",
            "do not reuse a localhost port from an older run",
            "semantic assertions for the UI states required",
            "record `viewport=` and matching `viewport_actual=`",
            "record `artifact_dir=` plus a `fit=` assertion",
            "strict outer wall-clock timeout",
            "do not start another unbounded browser run",
            "Every long-running helper started for E2E",
            "unmanifested listener from the current run is an environment gate cleanup failure",
            "interactive approval prompt",
            "Do not remain in a repeated MCP approval loop",
            "switch to Playwright CLI, Browser tooling, DOM/API probes, screenshots",
            "Do not claim \"no MCP failure observed\" unless",
            "Ignore `colab-mcp` startup failures when they are unrelated",
            "including Playwright, memory, or browser/evidence tools",
        ):
            self.assertIn(phrase, normalized)

    def test_zero_issue_runs_must_finalize_and_self_exit_without_extra_nudges(self) -> None:
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
        task_skill = " ".join(
            (CODEX / "skills" / "agent-orchestra-task-file" / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )

        for phrase in (
            "Zero-issue finalization is an action, not a narrative conclusion",
            "all reviewers report no blocking objection",
            "sync those files into the generated `AgentOrchestra/` copy",
            "write `[status] done`",
            "submit the documented self-exit as the next and final action",
            "Do not mark the persistent goal complete, send a normal final report",
            "MainAgent pane actually closing is part of the evidence",
            "Do not wait for a Hook wake, another reviewer nudge, or a user prompt",
        ):
            self.assertIn(phrase, main_template)
        for phrase in (
            "When the final sweep finds zero in-scope issues",
            "MainAgent must attempt to launch the smallest sufficient independent ProfessionalAgent team",
            "\"No active ProfessionalAgent panes are present\" is an observation, not a fallback rationale",
            "an empty `[Acceptance]`/`[Gates]` ledger while MainAgent continues into code audit is an orchestration defect",
            "before continuing with MainAgent-only source audit",
            "`blocking_objection=none`",
            "write `[status] done`, and, when the user required it",
            "persistent-goal completion message, or idle prompt is not enough",
            "The MainAgent pane must actually leave",
            "Do not wait for another Hook wake, peer nudge, or user reminder",
        ):
            self.assertIn(phrase, team_skill)
        for phrase in (
            "When review evidence shows zero remaining issues",
            "finalization must be the next state update",
            "Do not leave a finalizable task file at `[status] progress`",
        ):
            self.assertIn(phrase, task_skill)

    def test_professional_template_requires_evidence_before_ready_for_review(self) -> None:
        template = (
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(template.split())

        for phrase in (
            "Do not set `ready_for_review` merely because a local patch is complete",
            "after you have actually received and accepted the scoped assignment, set your own Agent state to `working`",
            "Do not set `working` for a blank/default composer",
            "the `[Acceptance]` requirement ids you addressed",
            "the evidence paths or pane references",
            "Preserve existing run-level `[Acceptance]`, `[Gates]`, and `[Candidates]`",
            "never replace the shared task file with a narrower review-only or specialist-only ledger",
            "\"Playwright MCP is missing\" does not make the visual gate optional",
            "strict outer wall-clock timeout",
            "do not retry with another unbounded browser run",
            "record the requested viewport and the measured viewport separately",
            "include a `fit=` assertion",
            "Every long-running helper you start for E2E",
            "unmanifested current-run listener",
            "Do not stop at \"the environment is missing\"",
            "Try repository-native setup, existing Docker compose",
            "If no autonomous route remains, report `needs_user` or a blocking objection",
            "Raise a blocking objection",
            "unstarted required environment",
            "missing required MCP/tool evidence",
            "same MCP approval prompt repeats",
            "switch to Playwright CLI, Browser tooling, DOM/API probes, screenshots",
            "Cannot find module '@playwright/test'",
            "No tests found",
            "plain Node script using `playwright`",
        ):
            self.assertIn(phrase, normalized)

    def test_environment_skill_documents_ephemeral_contract(self) -> None:
        skill = (CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        for phrase in (
            "AGENT_ORCHESTRA_CACHE_DIR",
            "AGENT_ORCHESTRA_ARTIFACT_DIR",
            "AGENT_ORCHESTRA_ENV_DIR",
            "flake.nix",
            "Docker compose",
            "COMPOSE_PROJECT_NAME=agent-orchestra-",
            "derive the primary verification environment from the product's documented or implemented use case",
            "Use desktop, mobile, responsive, small-screen, or other platform coverage only when it is explicitly in scope",
            "Do not turn out-of-scope platform coverage into an implementation target or completion gate",
            "Do not mark visual/E2E gates passed from code inspection alone",
            "stop and remove compose resources",
            "Environment failure is a problem to route around",
            "Keep `[status] progress` while any autonomous completion route remains",
            "exact missing credential, approval, network access, service, hardware, or scope change",
            "Do not remove arbitrary untracked repository files",
            "Do not delete `AGENT_ORCHESTRA_RUN_DIR` itself",
            "shared task files",
            "Agent `state.json`",
            "specific runtime resources",
            "Treat unknown local artifacts as evidence or candidates",
            "AGENT_ORCHESTRA_SERVER_MANIFEST",
            "AGENT_ORCHESTRA_SERVER_PORT",
            "process group id, base URL, port, and log path",
            "server_process start",
            "server_process stop",
            "private `stop_file`",
            "original supervisor can terminate its own child process",
            "stale or mismatched `base_url`",
            "matching `viewport=` and `viewport_actual=`",
            "record `artifact_dir=`",
            "Include `fit=` evidence",
            "requested/measured viewport mismatch",
            "Fake LLM/API servers",
            "unmanifested current-run listener",
            "bounded approval attempt",
            "pending MCP approval prompt is not a reason to leave dev servers",
            "probe the target application's action schema or API contract",
            "same MCP server asks for repeated approval prompts",
            "switch to Playwright CLI, Browser tooling, DOM/API probes, screenshots",
            "Browser evidence routes need an outer wall-clock timeout",
            "Do not assume `npx -p playwright node -e` exposes the package",
            "Do not assume GNU `timeout`, `pgrep`, or unrestricted process listing exists on macOS",
            "same `HOME` and cache environment",
            "PLAYWRIGHT_BROWSERS_PATH",
            "top-level `const`/`let` redeclarations",
            "Cannot find module '@playwright/test'",
            "No tests found",
            "server_process stop-all",
            "orphan-process candidate",
        ):
            self.assertIn(phrase, normalized)

    def test_agents_must_route_around_missing_environment_before_escalating(self) -> None:
        surfaces = [
            (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md").read_text(
                encoding="utf-8"
            ),
            (CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md").read_text(
                encoding="utf-8"
            ),
            (CODEX / "skills" / "agent-orchestra-team" / "SKILL.md").read_text(encoding="utf-8"),
            (CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md").read_text(encoding="utf-8"),
            (ROOT / "SPEC.md").read_text(encoding="utf-8"),
            (ROOT / "README.md").read_text(encoding="utf-8"),
        ]
        normalized_surfaces = [" ".join(surface.split()) for surface in surfaces]

        for surface in normalized_surfaces:
            for phrase in (
                "existing Docker compose",
                "ephemeral",
                "alternate",
                "needs_user",
                "credential, approval, network access, service, hardware, or scope change",
                "MachPortRendezvous",
                'sandbox_permissions="require_escalated"',
            ):
                self.assertIn(phrase, surface)

    def test_cleanup_preserves_unknown_local_artifacts(self) -> None:
        surfaces = [
            (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md").read_text(
                encoding="utf-8"
            ),
            (CODEX / "skills" / "agent-orchestra-team" / "SKILL.md").read_text(encoding="utf-8"),
            (CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md").read_text(encoding="utf-8"),
            (ROOT / "SPEC.md").read_text(encoding="utf-8"),
            (ROOT / "README.md").read_text(encoding="utf-8"),
        ]
        for surface in (" ".join(item.split()) for item in surfaces):
            for phrase in (
                "supervisor status",
                "`result`/`result-*`",
                "current-run",
                "unknown local artifacts",
            ):
                self.assertIn(phrase, surface)
        for surface in (
            " ".join(
                (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md")
                .read_text(encoding="utf-8")
                .split()
            ),
            " ".join(
                (CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md")
                .read_text(encoding="utf-8")
                .split()
            ),
        ):
            for phrase in (
                "Do not delete",
                "shared task file",
                "artifacts, logs, or evidence",
            ):
                self.assertIn(phrase, surface)

    def test_auxiliary_e2e_services_must_be_manifested_and_cleaned(self) -> None:
        surfaces = [
            (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md").read_text(
                encoding="utf-8"
            ),
            (CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md").read_text(
                encoding="utf-8"
            ),
            (CODEX / "skills" / "agent-orchestra-team" / "SKILL.md").read_text(encoding="utf-8"),
            (CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md").read_text(
                encoding="utf-8"
            ),
            (ROOT / "SPEC.md").read_text(encoding="utf-8"),
            (ROOT / "README.md").read_text(encoding="utf-8"),
        ]

        for surface in (" ".join(item.split()).casefold() for item in surfaces):
            for phrase in (
                "LLM/API servers",
                "PID/PGID",
                "port/base_url",
                "cleanup command",
                "unmanifested",
                "environment gate",
            ):
                self.assertIn(phrase.casefold(), surface)

if __name__ == "__main__":
    unittest.main()
