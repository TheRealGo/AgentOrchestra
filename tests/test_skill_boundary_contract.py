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
        self.assertIn("slow Codex TUI startup", common)
        self.assertIn("peer still finishing its current turn", common)
        self.assertIn("not supervision", common)
        self.assertIn("returns non-zero if the target Codex TUI does not accept the message", common_normalized)
        self.assertIn("If the helper exits non-zero, do not continue as if the message was delivered", common)
        self.assertIn("Raw `tmux send-keys` is limited to shell launch commands, `/exit`", common)
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
        self.assertIn("split-window", main)
        self.assertIn("agent-orchestra-launch", main)
        self.assertIn("kill-pane", main)
        self.assertIn("not a hard permission boundary", main)

    def test_task_file_skill_documents_empty_done_vs_active_progress(self) -> None:
        task = (CODEX / "skills" / "agent-orchestra-task-file" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(task.split())

        self.assertIn("initializes a quiet empty task file with `[status] done`", normalized)
        self.assertIn("switch the file to `[status] progress`", normalized)
        self.assertIn("discovery, investigation, implementation, or review work", normalized)
        self.assertIn("Backlog/InProgress/InReview/Candidates/Done state", normalized)
        self.assertIn("Candidate ids must be unique", normalized)
        self.assertIn("Candidate field keys", normalized)
        self.assertIn("must not be duplicated", normalized)
        self.assertIn("duplicate keys make the candidate unresolved", normalized)
        self.assertIn("Every completed candidate must include a non-empty id", normalized)
        self.assertIn("a `summary`, and an `evidence` pointer", normalized)

    def test_tmux_main_skill_documents_retirement_cleanup_sequence(self) -> None:
        main = (CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(main.split())

        for phrase in (
            "Write that ProfessionalAgent state to `retired`",
            "Send `/exit`",
            "Do not skip this step",
            "`kill-pane` is only cleanup after an attempted `/exit`",
            "Verify pane cleanup and use `kill-pane`",
            "Set `retired` before `/exit`",
            "Retirement is not complete until the pane is gone",
            "capture any final output and force-close it",
            "Do not finish a run with accepted ProfessionalAgent panes still present",
            "does not replace pane cleanup",
        ):
            self.assertIn(phrase, normalized)

        self.assertIn('tmux send-keys -t "$PANE" "/exit" "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"', main)
        self.assertIn("tmux list-panes -a -F '#{pane_id}' | rg -qxF \"$PANE\"", main)
        self.assertIn('tmux capture-pane -t "$PANE" -p -S -120', main)
        self.assertIn('tmux kill-pane -t "$PANE"', main)

    def test_tmux_main_skill_documents_requested_mainagent_self_exit(self) -> None:
        main = (CODEX / "skills" / "agent-orchestra-tmux-main" / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(main.split())

        for phrase in (
            "If the user explicitly instructed MainAgent to leave the orchestra",
            "submit `/exit` to MainAgent's own pane as the final tmux action",
            "Do not use delayed or background self-exit shell jobs",
            "Use a detached Python self-exit as the final tool action",
            'subprocess.run(["tmux", "send-keys", "-t", pane, "/exit", submit_key]',
            'subprocess.run(["tmux", "send-keys", "-t", pane, submit_key]',
            "report the failure explicitly",
            "Do not claim that MainAgent exited",
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
            "Use the bounded detached Python self-exit procedure",
            "documented by the `agent-orchestra-tmux-main` Skill as the final tool action",
            "report the explicit self-exit failure",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
