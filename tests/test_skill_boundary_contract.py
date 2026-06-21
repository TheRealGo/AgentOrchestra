from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"


class SkillBoundaryContractTests(unittest.TestCase):
    def test_launch_skill_uses_protocol_layers_for_professional_agents(self) -> None:
        launch = (CODEX / "skills" / "agent-orchestra-launch" / "SKILL.md").read_text(encoding="utf-8")
        launch_normalized = " ".join(launch.split())

        self.assertIn("--protocol-layer \"08\"", launch)
        self.assertIn("$AGENT_ORCHESTRA_REPO_ROOT/layers", launch_normalized)
        self.assertIn("not from the target project", launch_normalized)
        self.assertIn("Do not use the target project's `layers/` tree", launch_normalized)
        self.assertIn("single quotes when invoking `prepare_agent_launch.py`", launch_normalized)
        self.assertIn("Do not recompose the Codex launch command by hand", launch_normalized)
        self.assertIn("Before pasting any shell launch command, capture the target pane", launch_normalized)
        self.assertIn("clearly outside Codex TUI", launch_normalized)
        self.assertIn("Do not paste a launch command into a pane that still shows a Codex composer", launch_normalized)
        self.assertIn("initializes `state.json` as `ready`", launch_normalized)
        self.assertIn("Delivery confirmation, not pane creation or TUI startup", launch_normalized)
        self.assertIn("background terminal status", launch_normalized)
        self.assertIn("prompt pollution", launch_normalized)
        self.assertIn("`command.json` is the runtime boundary for the full argv", launch_normalized)
        self.assertIn("--enable prevent_idle_sleep", launch_normalized)
        self.assertIn("Path(sys.argv[1])", launch)
        self.assertIn("Do not depend on pane-local shell variables", launch_normalized)
        self.assertIn("shell-quoted final Python argument", launch_normalized)
        self.assertIn("Library/Application Support", launch_normalized)
        self.assertIn("/Users/.../Library/Application/command.json", launch_normalized)
        self.assertIn("'\"'\"'/path/from/helper/output'\"'\"'", launch)
        self.assertNotIn('Path(os.environ["AGENT_DIR"])', launch)
        self.assertIn("env.json", launch)
        self.assertIn("os.execvpe", launch)
        self.assertIn("parent shell environment", launch_normalized)
        self.assertIn("tokens", launch_normalized)
        self.assertNotIn("codex --profile agent-orchestra --ask-for-approval never", launch)
        self.assertNotIn("--instruction-source \"$AGENT_ORCHESTRA_TARGET_PROJECT", launch)
        self.assertNotIn("AGENT_ORCHESTRA_TARGET_PROJECT/layers", launch)
        self.assertNotIn("${AGENT_ORCHESTRA_TARGET_PROJECT}/layers", launch)
        self.assertNotIn("target_project/layers", launch)

    def test_tmux_skills_are_split_by_common_and_main_operations(self) -> None:
        common = (CODEX / "skills" / "agent-orchestra-tmux-common" / "SKILL.md").read_text(encoding="utf-8")
        main = (CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md").read_text(encoding="utf-8")
        common_normalized = " ".join(common.split())
        main_normalized = " ".join(main.split())

        self.assertIn("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", common_normalized)
        self.assertIn("Do not prepend `Space`", common_normalized)
        self.assertNotIn("Space C-j", common_normalized)
        self.assertIn("$AGENT_ORCHESTRA_TMUX_PANE", common_normalized)
        self.assertIn("Do not infer your own pane from a bare `tmux display-message`", common_normalized)
        self.assertIn("Pasting text into the composer is not delivery", common)
        self.assertIn("agent_orchestra_minimal.tmux_send", common)
        self.assertIn("Use the runtime delivery helper for initial tasks", common)
        self.assertIn("follow-up messages, review requests", common_normalized)
        self.assertIn("ProfessionalAgent-to-ProfessionalAgent consultation", common)
        self.assertIn("--poll-interval-seconds 0.5", common)
        self.assertIn("--polls-per-attempt 60", common)
        self.assertIn("--result-json", common)
        self.assertIn("degraded delivery", common)
        self.assertIn("--allow-short-polls", common)
        self.assertIn("optional peer consultation", common_normalized)
        self.assertIn("Do not use short polling for initial ProfessionalAgent assignments", common)
        self.assertIn("slow Codex TUI startup", common)
        self.assertIn("peer still finishing its current turn", common)
        self.assertIn("before pasting", common)
        self.assertIn("without interrupting the active conversation", common)
        self.assertIn("not supervision", common)
        self.assertIn("returns non-zero if the target Codex TUI does not accept the message", common_normalized)
        self.assertIn("If the helper exits non-zero, do not continue as if the message was delivered", common)
        self.assertIn("record the attempted consultation or review request", common_normalized)
        self.assertIn("not delivered", common_normalized)
        self.assertIn("Raw `tmux send-keys` is limited to shell launch commands, `/exit`", common)
        self.assertIn("delivery helper with `--allow-interrupted-recovery`", common)
        self.assertIn("Do not use `--allow-interrupted-recovery` for initial assignments", common)
        self.assertIn("only for explicit recovery instructions", common)
        self.assertIn("interrupted, paused, or blocked", common)
        self.assertNotIn("For short one-line messages", common)
        self.assertNotIn("MainAgent: please investigate", common)
        self.assertIn("capture-pane", common)
        self.assertIn("Consultation Evidence", common)
        self.assertIn("ProfessionalAgent <-> ProfessionalAgent", common)
        self.assertIn("sender and receiver pane/agent id", common)
        self.assertIn("topic, question, objection, or requested review", common)
        self.assertIn("response, timeout, or unanswered state", common)
        self.assertIn("disposition: accepted, rejected, deferred, request-changes, or block", common)
        self.assertIn("evidence pointer or reason", common)
        self.assertIn("request-changes, or block", common)
        self.assertNotIn("split-window", common)

        self.assertIn("MainAgent manages ProfessionalAgent panes", main)
        self.assertIn("task, follow-up, and review message delivery", main)
        self.assertIn("concrete send/capture/retry procedure", main_normalized)
        self.assertIn("scoped initial task", main)
        self.assertIn("state starts as `ready`", main_normalized)
        self.assertIn("do not change it to `working` until the scoped assignment delivery is confirmed", main_normalized)
        self.assertIn("split-window", main)
        self.assertIn('MAIN_PANE="${AGENT_ORCHESTRA_TMUX_PANE:?}"', main)
        self.assertIn('tmux split-window -h -t "$MAIN_PANE"', main)
        self.assertIn('tmux split-window -v -t "$PRO_PANE_1"', main)
        self.assertIn("Never rely on tmux's current active client", main)
        self.assertIn("agent-orchestra-launch", main)
        self.assertIn("kill-pane", main)
        self.assertIn("not a hard permission boundary", main)

    def test_task_file_skill_documents_empty_done_vs_active_progress(self) -> None:
        task = (CODEX / "skills" / "agent-orchestra-task-file" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(task.split())

        self.assertIn("can initialize a quiet empty task file with `[status] done`", normalized)
        self.assertIn("Legacy task files that omit those two sections are parsed as empty acceptance/gate ledgers", normalized)
        self.assertIn("do not \"fix\" that compatibility by making old task files invalid", normalized)
        self.assertIn("receiving a user task starts and stays `[status] progress`", normalized)
        self.assertIn("discovery, investigation, implementation, or review work", normalized)
        self.assertIn("Backlog/InProgress/InReview/Acceptance/Gates/Candidates/Done state", normalized)
        self.assertIn("Candidate ids must be unique", normalized)
        self.assertIn("Candidate field keys", normalized)
        self.assertIn("must not be duplicated", normalized)
        self.assertIn("duplicate keys make the candidate unresolved", normalized)
        self.assertIn("Every completed candidate must include a non-empty id", normalized)
        self.assertIn("a `summary`, and an `evidence` pointer", normalized)
        self.assertIn("Preserve existing run-level `[Acceptance]`, `[Gates]`, and `[Candidates]`", normalized)
        self.assertIn("Do not replace the shared task file with a narrower review-only", normalized)
        self.assertIn("Never \"simplify\" the shared file by regenerating it from your local notes", normalized)
        self.assertIn("verify that unrelated acceptance, gate, candidate, and peer state entries survived", normalized)
        self.assertIn("Do not add a `status` key to state JSON", normalized)
        self.assertIn("agent_orchestra_minimal.agent_state_update", normalized)

    def test_tmux_skills_document_confirmed_single_assignment_delivery(self) -> None:
        common = (CODEX / "skills" / "agent-orchestra-tmux-common" / "SKILL.md").read_text(encoding="utf-8")
        main = (CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md").read_text(encoding="utf-8")
        combined = " ".join((common + "\n" + main).split())

        self.assertIn("send the complete scoped task in one confirmed delivery", combined)
        self.assertIn("Do not send a preliminary \"receipt only\" message", combined)
        self.assertIn("default composer prompt", combined)
        self.assertIn("delivery is not confirmed", combined)
        self.assertIn("Before delivery, add the ProfessionalAgent work item to `[InProgress]`", combined)

    def test_professional_agent_launch_requires_verified_pane_identity(self) -> None:
        launch = (CODEX / "skills" / "agent-orchestra-launch" / "SKILL.md").read_text(encoding="utf-8")
        main = (CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md").read_text(encoding="utf-8")
        template = (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md").read_text(
            encoding="utf-8"
        )
        combined = " ".join((launch + "\n" + main + "\n" + template).split())

        for phrase in (
            "verify the exact pane identity",
            "current dedicated orchestra session",
            "pane_current_command",
            "pane_current_path",
            "must match `command.json` `cwd`",
            "MainAgent workspace",
            "failed ProfessionalAgent launch",
            "even if `state.json` says `ready`",
            "Do not send assignments",
            "echo launch-test",
            "paste-test",
            "launch-routing `[Candidates]` item",
            "do not launch more Agents",
            "verified session name",
            "Raw `tmux send-keys` is only for shell launch commands and `/exit`",
        ):
            self.assertIn(phrase, combined)

        self.assertIn("tmux display-message -p -t \"$PANE\"", combined)
        self.assertIn("#{pane_id} #{pane_current_command} #{pane_current_path}", combined)
        self.assertIn("do not continue launching more Agents from an unverified pane set", combined)

    def test_tmux_main_skill_documents_retirement_cleanup_sequence(self) -> None:
        main = (CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(main.split())

        for phrase in (
            "Write that ProfessionalAgent state to `retired`",
            "Send `/exit`",
            "Do not skip this step",
            "`kill-pane` is only cleanup after an attempted `/exit`",
            "packaged `agent_orchestra_minimal.self_exit` helper",
            "handles intermediate Codex prompts such as the Memories opt-in prompt",
            "Verify pane cleanup and use `kill-pane`",
            "Set `retired` before `/exit`",
            "Retirement is not complete until the pane is gone",
            "whether the pane id is still present",
            "Do not finish a run with accepted ProfessionalAgent panes still present",
            "does not replace pane cleanup",
        ):
            self.assertIn(phrase, normalized)

        self.assertIn('tmux send-keys -t "$PANE" "/exit" "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"', main)
        self.assertIn("if tmux list-panes -a -F '#{pane_id}' | rg -qxF \"$PANE\"; then", main)
        self.assertIn('tmux capture-pane -t "$PANE" -p -S -120', main)
        self.assertIn('tmux kill-pane -t "$PANE"', main)
        self.assertNotIn("verify\nthe pane id is absent", main)

    def test_tmux_main_skill_documents_requested_mainagent_self_exit(self) -> None:
        main = (CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(main.split())

        for phrase in (
            "If the user explicitly instructed MainAgent to leave the orchestra",
            "submit `/exit` to MainAgent's own pane as the final tmux action",
            "Do not use delayed or background self-exit shell jobs",
            "Use the packaged `agent_orchestra_minimal.self_exit` helper as the final tool action",
            "`pane_current_command` is still a Codex CLI command such as `node` or `codex`",
            "alternates `C-m`/`C-j` submit keys",
            "writes JSON evidence",
            "clears queued `/exit` text",
            "resolve the pane from Agent state `tmux_target`",
            "Do not fall back to a bare `tmux display-message` active-pane lookup",
            '"${AGENT_ORCHESTRA_PYTHON:-python3}"',
            "-m agent_orchestra_minimal.self_exit",
            "--result-path",
            "leak `/exit` into the shell prompt",
            "The helper's result file is the self-exit evidence",
            "Do not claim that MainAgent exited",
            "agent_orchestra_minimal.self_e2e_finalizer",
            "--task-file",
            "Do not rely on CAO cleanup, a post-exit Hook wake, or a separate proof session",
        ):
            self.assertIn(phrase, normalized)

    def test_main_template_documents_requested_mainagent_self_exit(self) -> None:
        template = (CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(template.split())

        for phrase in (
            "If the user explicitly says to leave the orchestra with `/exit`",
            "Do not invent ad hoc delayed or background shell self-exit jobs",
            "Use the packaged `agent_orchestra_minimal.self_exit` procedure",
            "documented by the `agent-orchestra-tmux-main` Skill as the final tool action",
            "read your Agent state `tmux_target` instead of using the active client pane",
            "resolve the pane from `AGENT_ORCHESTRA_TMUX_PANE` or Agent state `tmux_target`",
            "only send keys while `pane_current_command` is still a Codex CLI command such as `node` or `codex`",
            "must write JSON evidence",
            "must clear visible `/exit` leftovers",
            "Report the explicit self-exit failure",
            "without shell prompt input leftovers",
            "agent_orchestra_minimal.self_e2e_finalizer",
            "--task-file",
            "Do not rely on a separate post-exit wake",
            "Do not recompose the Codex launch command by hand",
            "feature flags such as `--enable prevent_idle_sleep`",
            "`command.json` is the source of truth",
            "use a neutral variable such as `rc=$?`",
            "`status` is a read-only zsh parameter",
            "a fixable AgentOrchestra defect observed during E2E is not final",
            "Add runtime, launch, tmux delivery, MCP/tooling, environment, or completion-contract defects to `[Backlog]`",
        ):
            self.assertIn(phrase, normalized)

    def test_professional_template_keeps_ready_work_in_review_until_accepted(self) -> None:
        template = (
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(template.split())

        for phrase in (
            "set your Agent state to `ready_for_review` before or as you report the result",
            "scoped task in the shared task file under `[InReview]`",
            "to `[Done]` only when the accepted disposition is known",
            "do not use this task update to decide whole-run completion",
            "agent_orchestra_minimal.agent_state_update",
            "Do not hand-write a `status` key",
        ):
            self.assertIn(phrase, normalized)

    def test_environment_skill_documents_http_health_identity_check(self) -> None:
        skill = (CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        self.assertIn("--health-url", skill)
        self.assertIn("--health-contains", normalized)
        self.assertIn("--allow-tcp-readiness", normalized)
        self.assertIn("never use it for a web/API server just to bypass a missing health check", normalized)
        self.assertIn("stale localhost listener from an earlier run cannot satisfy the readiness gate", normalized)

    def test_team_skill_keeps_fixable_orchestra_defects_in_progress(self) -> None:
        skill = (CODEX / "skills" / "agent-orchestra-team" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(skill.split())

        self.assertIn("do not mark a fixable AgentOrchestra runtime", normalized)
        self.assertIn("add the defect to `[Backlog]`, keep `[status] progress`", normalized)
        self.assertIn("require later verification before changing that candidate to `integrated`", normalized)
        self.assertIn("focused unit regressions are not enough", normalized)
        self.assertIn("require a later clean live E2E", normalized)


if __name__ == "__main__":
    unittest.main()
