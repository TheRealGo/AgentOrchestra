from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402
from agent_orchestra_minimal.pane_manifest import PaneRecord, resume_decision  # noqa: E402
from agent_orchestra_minimal.tmux_send import send_text  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class PreviousE2ERuntimeRegressionTests(unittest.TestCase):
    def test_tmux_send_rejects_partial_prompt_tail_after_old_started_marker(self) -> None:
        message = (
            "ProfessionalAgent pro-layer08-runtime -> pro-layer15-qa: please "
            "review runtime implementation and raise blocking objections on prior E2E issues."
        )
        capture = (
            f"› {message}\n\n"
            "• Working\n\n"
            "─ Worked for 5m 28s ───────────────────\n\n"
            "› objections on prior E2E issues.\n\n"
            "  gpt-5.5 default · ${HOME}/Library/...\n"
        )
        fake = FakeTmuxSend(captures=[capture], baseline_capture="› Run /review on my current changes\n")

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_tmux_send_accepts_exact_short_agent_prompt_with_visible_started_work(self) -> None:
        message = "MainAgent: review now"
        fake = FakeTmuxSend(
            captures=[f"› {message}\n\n• Working\n"],
            baseline_capture="› Find and fix a bug in @filename\n",
        )

        result = send_text(
            "%8",
            message,
            runner=fake,
            max_retries=0,
            poll_interval_seconds=0,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 1)

    def test_nested_copy_edit_root_stays_scoped_when_protocol_root_is_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repo"
            target = root / "AgentOrchestra"
            target.mkdir(parents=True)
            subprocess.run(["git", "init", str(root)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            root = root.resolve()
            target = target.resolve()

            with patch.dict(os.environ, {"AGENT_ORCHESTRA_REPO_ROOT": str(root)}, clear=False):
                material = prepare_launch_material(
                    run_dir=Path(tmpdir) / "run",
                    agent_id="pro-nested-copy",
                    agent_kind="ProfessionalAgent",
                    target_project=target,
                    instruction_text="Layer instruction.",
                )

            argv = list(material.command["argv"])
            add_dirs = [argv[index + 1] for index, value in enumerate(argv) if value == "--add-dir"]
            self.assertEqual(material.env["AGENT_ORCHESTRA_REPO_ROOT"], str(root))
            self.assertEqual(material.env["AGENT_ORCHESTRA_TARGET_PROJECT"], str(target))
            self.assertEqual(material.env["AGENT_ORCHESTRA_EDIT_ROOT"], str(target))
            self.assertEqual(material.env["AGENT_ORCHESTRA_ACCESS_ROOTS"].split(os.pathsep), [str(target)])
            self.assertEqual(add_dirs[0], str(target))
            self.assertIn(str(material.run_dir), add_dirs)
            self.assertNotIn(str(root), add_dirs)

    def test_selfe2e_professional_agent_launch_uses_never_approval_without_parent_add_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repo"
            target = root / "AgentOrchestra"
            (target / ".tmp" / "self-improvement-e2e").mkdir(parents=True)
            (target / ".codex" / "agent_orchestra_minimal").mkdir(parents=True)
            (target / ".codex" / "skills").mkdir(parents=True)
            (target / ".codex" / "hooks").mkdir(parents=True)
            (target / ".tmp" / "self-improvement-e2e" / "status").write_text("progress", encoding="utf-8")
            subprocess.run(["git", "init", str(root)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            root = root.resolve()
            target = target.resolve()

            with patch.dict(os.environ, {"AGENT_ORCHESTRA_REPO_ROOT": str(root)}, clear=False):
                material = prepare_launch_material(
                    run_dir=Path(tmpdir) / "run",
                    agent_id="pro-selfe2e-round4",
                    agent_kind="ProfessionalAgent",
                    target_project=target,
                    instruction_text="Layer instruction.",
                    tmux_pane="%349",
                )

            argv = list(material.command["argv"])
            add_dirs = [argv[index + 1] for index, value in enumerate(argv) if value == "--add-dir"]
            self.assertEqual(argv[argv.index("--ask-for-approval") + 1], "never")
            self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
            self.assertEqual(material.env["AGENT_ORCHESTRA_TARGET_PROJECT"], str(target))
            self.assertEqual(material.env["AGENT_ORCHESTRA_EDIT_ROOT"], str(target))
            self.assertEqual(add_dirs[0], str(target))
            self.assertIn(str(target / ".codex"), add_dirs)
            self.assertIn(str(target / ".codex" / "agent_orchestra_minimal"), add_dirs)
            self.assertIn(str(material.run_dir), add_dirs)
            self.assertNotIn(str(root), add_dirs)

    def test_service_e2e_stale_panes_are_quarantined_and_duplicate_active_panes_require_disambiguation(self) -> None:
        stale_decision = resume_decision(
            [
                PaneRecord("main-recovery", "%11", "unsupported_model", "checkpoint-old"),
                PaneRecord("main", "%12", "interrupted_or_paused", "checkpoint-new"),
            ]
        )
        self.assertEqual(stale_decision.active, ())
        self.assertEqual([record.pane for record in stale_decision.quarantine], ["%11", "%12"])
        self.assertEqual(
            stale_decision.strategy,
            "launch_recovery_from_latest_checkpoint_and_keep_stale_panes_quarantined",
        )

        duplicate_decision = resume_decision(
            [
                PaneRecord("main", "%21", "working", "checkpoint-a"),
                PaneRecord("main-duplicate", "%22", "ready", "checkpoint-b"),
            ]
        )
        self.assertEqual(duplicate_decision.strategy, "requires_mainagent_disambiguation_before_resume")
        self.assertEqual([record.pane for record in duplicate_decision.active], ["%21", "%22"])


if __name__ == "__main__":
    unittest.main()
