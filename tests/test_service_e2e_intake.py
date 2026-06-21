from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.service_e2e_intake import (  # noqa: E402
    ServiceE2EDefect,
    append_self_improvement_intake_to_task_file,
    render_self_improvement_intake,
    render_self_improvement_intake_from_brief,
    render_service_e2e_approval_replay_intake,
)
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE, SharedTaskFile  # noqa: E402


class ServiceE2EIntakeTests(unittest.TestCase):
    def test_service_defect_intake_renders_backlog_acceptance_gate_and_candidate(self) -> None:
        rendered = render_self_improvement_intake(
            ServiceE2EDefect(
                defect_id="AO-Usage-Limit",
                symptom="usage limit left stale main-recovery pane and ambiguous active run",
                workaround="CAO inspected panes and chose the active one manually",
                desired_behavior="maintain active pane manifest, checkpoint, and quarantine stale panes",
                expected_regression="focused regression verifies manifest checkpoint and stale pane quarantine",
            )
        )

        self.assertIn("ao-usage-limit", rendered["Backlog"])
        self.assertIn("owner_dri=main", rendered["Backlog"])
        self.assertIn("status=open", rendered["Acceptance"])
        self.assertIn("source=service-e2e-defect", rendered["Acceptance"])
        self.assertIn("kind=e2e", rendered["Gates"])
        self.assertIn("disposition=open", rendered["Candidates"])

    def test_service_defect_intake_rejects_incomplete_observations(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected_regression is required"):
            render_self_improvement_intake(
                ServiceE2EDefect(
                    defect_id="ao-delivery",
                    symptom="composer residue merged with recovery wake",
                    workaround="CAO cleared composer",
                    desired_behavior="archive and clear residue before sending",
                    expected_regression="",
                )
            )

    def test_service_defect_id_must_be_ledger_safe(self) -> None:
        with self.assertRaisesRegex(ValueError, "defect_id"):
            render_self_improvement_intake(
                ServiceE2EDefect(
                    defect_id="ao:delivery",
                    symptom="composer residue",
                    workaround="manual clear",
                    desired_behavior="clear residue",
                    expected_regression="focused regression",
                )
            )

    def test_service_defect_brief_renders_self_e2e_backlog_acceptance(self) -> None:
        rendered = render_self_improvement_intake_from_brief(
            """
            ServiceE2E found completion profile drift, task file malformed gates,
            tmux composer residue, approval/UserNeeded overuse, usage limit stale
            pane recovery, and missing ServiceE2E defect intake.
            """
        )

        joined = "\n".join(line for lines in rendered.values() for line in lines)
        self.assertIn("completion-profile-user-intent-gates", joined)
        self.assertIn("task-file-finalization-validation", joined)
        self.assertIn("tmux-delivery-confirmation", joined)
        self.assertIn("approval-userneeded-classification", joined)
        self.assertIn("usage-limit-pane-recovery", joined)
        self.assertIn("source=service-e2e-defect", joined)
        self.assertIn("disposition=open", joined)

    def test_service_e2e_approval_replay_intake_preserves_all_nine_observations(self) -> None:
        rendered = render_service_e2e_approval_replay_intake()

        for section in ("Backlog", "Acceptance", "Gates", "Candidates"):
            self.assertEqual(len(rendered[section]), 9, section)

        joined = "\n".join(line for lines in rendered.values() for line in lines)
        for defect_id in (
            "chromium-firefox-matrix",
            "ios-simulator-smoke",
            "ios-build-smoke",
            "mobile-route-evidence",
            "mobile-interactive-evidence",
            "browser-evidence-rerun",
            "chromium-firefox-matrix-port",
            "run-scoped-process-cleanup",
            "run-scoped-docker-volume-cleanup",
        ):
            self.assertIn(f"service-e2e-approval-replay-{defect_id}", joined)
            self.assertIn(f"service-e2e-approval-replay:{defect_id}", joined)
        self.assertEqual(joined.count("approval prompt disposition autonomy_blocker"), 18)
        self.assertEqual(joined.count("UserNeeded disposition autonomy_blocker"), 18)

    def test_service_e2e_brief_with_approval_cleanup_renders_replay_items(self) -> None:
        rendered = render_self_improvement_intake_from_brief(
            "ServiceE2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases."
        )

        joined = "\n".join(line for lines in rendered.values() for line in lines)
        self.assertIn("service-e2e-approval-replay-browser-evidence-rerun", joined)
        self.assertIn("service-e2e-approval-replay-run-scoped-docker-volume-cleanup", joined)
        self.assertIn("approval prompt routes through UserNeeded disposition autonomy_blocker", joined)

    def test_hyphenated_service_e2e_brief_with_approval_cleanup_renders_replay_items(self) -> None:
        rendered = render_self_improvement_intake_from_brief(
            "Service-E2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases."
        )

        joined = "\n".join(line for lines in rendered.values() for line in lines)
        self.assertIn("service-e2e-approval-replay-browser-evidence-rerun", joined)
        self.assertIn("service-e2e-approval-replay-run-scoped-docker-volume-cleanup", joined)

    def test_service_e2e_intake_appends_to_task_file_and_keeps_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_file = Path(tmp) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")

            append_self_improvement_intake_to_task_file(
                task_file_path=task_file,
                defect_brief="ServiceE2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases.",
            )

            parsed = SharedTaskFile.read(task_file)
            self.assertEqual(parsed.status, "progress")
            self.assertEqual(len(parsed.sections["Backlog"]), 10)
            self.assertEqual(len(parsed.sections["Acceptance"]), 10)
            self.assertEqual(len(parsed.sections["Gates"]), 10)
            self.assertEqual(len(parsed.sections["Candidates"]), 10)
            joined = task_file.read_text(encoding="utf-8")
            self.assertIn("approval-userneeded-classification-acceptance", joined)
            self.assertIn("service-e2e-approval-replay-browser-evidence-rerun", joined)
            self.assertIn("approval prompt routes through UserNeeded disposition autonomy_blocker", joined)

    def test_service_e2e_intake_append_is_duplicate_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_file = Path(tmp) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
            brief = "ServiceE2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases."

            append_self_improvement_intake_to_task_file(task_file_path=task_file, defect_brief=brief)
            append_self_improvement_intake_to_task_file(task_file_path=task_file, defect_brief=brief)

            parsed = SharedTaskFile.read(task_file)
            self.assertEqual(len(parsed.sections["Backlog"]), 10)
            self.assertEqual(len(parsed.sections["Candidates"]), 10)

    def test_service_e2e_intake_append_refreshes_existing_generated_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_file = Path(tmp) / "tasks.ini"
            task_file.write_text(
                DEFAULT_TASK_FILE.replace(
                    "[Acceptance]\n\n",
                    (
                        "[Acceptance]\n"
                        "service-e2e-approval-replay-browser-evidence-rerun-acceptance: "
                        "status=open; source=service-e2e-defect; owner=main; "
                        "verification=old replay wording; evidence=pending\n\n"
                    ),
                ),
                encoding="utf-8",
            )

            append_self_improvement_intake_to_task_file(
                task_file_path=task_file,
                defect_brief="ServiceE2E exposed nine approval/UserNeeded/cleanup CAO-intervention cases.",
            )

            parsed = SharedTaskFile.read(task_file)
            browser_items = [
                item
                for item in parsed.sections["Acceptance"]
                if item.startswith("service-e2e-approval-replay-browser-evidence-rerun-acceptance:")
            ]
            self.assertEqual(len(browser_items), 1)
            self.assertIn("approval prompt routes through UserNeeded disposition autonomy_blocker", browser_items[0])


if __name__ == "__main__":
    unittest.main()
