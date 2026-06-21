from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.rekick import decide_wake  # noqa: E402
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE, SharedTaskFile  # noqa: E402


LEGACY_TASK_FILE = """\
[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]

[Done]
completed item
"""


class CompletionGateContractTests(unittest.TestCase):
    def test_default_task_file_includes_acceptance_and_gates(self) -> None:
        task_file = SharedTaskFile.parse(DEFAULT_TASK_FILE)

        self.assertIn("Acceptance", task_file.sections)
        self.assertIn("Gates", task_file.sections)
        self.assertFalse(task_file.has_unresolved_acceptance)
        self.assertFalse(task_file.has_unresolved_gates)

    def test_legacy_task_file_treats_missing_new_sections_as_empty(self) -> None:
        task_file = SharedTaskFile.parse(LEGACY_TASK_FILE)

        self.assertEqual(task_file.sections["Acceptance"], [])
        self.assertEqual(task_file.sections["Gates"], [])
        self.assertTrue(task_file.is_finalized)

    def test_unresolved_acceptance_and_gates_block_finalization(self) -> None:
        text = DEFAULT_TASK_FILE.replace(
            "[Acceptance]\n\n",
            "[Acceptance]\nREQ-001: status=open; source=user; owner=main; verification=ui; evidence=pending\n\n",
        ).replace(
            "[Gates]\n\n",
            "[Gates]\ngate-visual: status=failed; kind=visual; evidence=artifacts/desktop.png\n\n",
        )

        task_file = SharedTaskFile.parse(text)

        self.assertFalse(task_file.is_finalized)
        self.assertIn(
            "acceptance:REQ-001: status=open; source=user; owner=main; verification=ui; evidence=pending",
            task_file.finalization_blockers,
        )
        self.assertIn(
            "gate:gate-visual: status=failed; kind=visual; evidence=artifacts/desktop.png",
            task_file.finalization_blockers,
        )

    def test_resolved_acceptance_and_gate_statuses_allow_finalization(self) -> None:
        for acceptance_status in ("satisfied", "out-of-scope", "deferred"):
            for gate_status in ("passed", "not-applicable"):
                with self.subTest(acceptance=acceptance_status, gate=gate_status):
                    task_file = SharedTaskFile.parse(
                        DEFAULT_TASK_FILE.replace(
                            "[Acceptance]\n\n",
                            (
                                "[Acceptance]\n"
                                f"REQ-001: status={acceptance_status}; source=user; "
                                "owner=main; verification=tests; evidence=artifacts/report.txt\n\n"
                            ),
                        ).replace(
                            "[Gates]\n\n",
                            f"[Gates]\ngate-test: status={gate_status}; kind=test; evidence=tests\n\n",
                        )
                    )

                    self.assertTrue(task_file.is_finalized)

    def test_blocked_and_needs_user_ledgers_keep_status_progress(self) -> None:
        task_file = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Acceptance]\n\n",
                (
                    "[Acceptance]\n"
                    "REQ-001: status=blocked; source=user; owner=main; "
                    "verification=visual; evidence=browser unavailable\n"
                    "REQ-002: status=needs_user; source=user; owner=main; "
                    "verification=credentialed smoke; evidence=needs API key\n\n"
                ),
            ).replace(
                "[Gates]\n\n",
                (
                    "[Gates]\n"
                    "gate-visual: status=blocked; kind=visual; evidence=browser unavailable\n"
                    "gate-mcp: status=needs_user; kind=mcp; evidence=approval required\n\n"
                ),
            )
        )

        self.assertFalse(task_file.is_finalized)
        self.assertEqual(
            task_file.finalization_blockers,
            [
                "acceptance:REQ-001: status=blocked; source=user; owner=main; verification=visual; evidence=browser unavailable",
                "acceptance:REQ-002: status=needs_user; source=user; owner=main; verification=credentialed smoke; evidence=needs API key",
                "gate:gate-visual: status=blocked; kind=visual; evidence=browser unavailable",
                "gate:gate-mcp: status=needs_user; kind=mcp; evidence=approval required",
            ],
        )

    def test_missing_required_fields_or_unknown_gate_kind_are_blockers(self) -> None:
        task_file = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Acceptance]\n\n",
                "[Acceptance]\nREQ-001: status=satisfied; source=user; owner=main; evidence=tests\n\n",
            ).replace(
                "[Gates]\n\n",
                "[Gates]\ngate-ui: status=passed; kind=unknown; evidence=shot.png\n\n",
            )
        )

        self.assertTrue(task_file.has_unresolved_acceptance)
        self.assertTrue(task_file.has_unresolved_gates)

    def test_duplicate_acceptance_and_gate_field_keys_block_finalization(self) -> None:
        task_file = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Acceptance]\n\n",
                (
                    "[Acceptance]\n"
                    "REQ-001: status=satisfied; status=deferred; source=user; "
                    "owner=main; verification=tests; evidence=tests\n\n"
                ),
            ).replace(
                "[Gates]\n\n",
                (
                    "[Gates]\n"
                    "gate-test: status=passed; kind=test; kind=e2e; evidence=tests\n\n"
                ),
            )
        )

        self.assertFalse(task_file.is_finalized)
        self.assertEqual(
            task_file.finalization_blockers,
            [
                "acceptance:REQ-001: status=satisfied; status=deferred; source=user; "
                "owner=main; verification=tests; evidence=tests",
                "gate:gate-test: status=passed; kind=test; kind=e2e; evidence=tests",
            ],
        )

    def test_resolved_acceptance_and_gates_require_non_placeholder_evidence(self) -> None:
        placeholders = ("pending", "TBD", "todo", "unknown")

        for evidence in placeholders:
            with self.subTest(evidence=evidence):
                task_file = SharedTaskFile.parse(
                    DEFAULT_TASK_FILE.replace(
                        "[Acceptance]\n\n",
                        (
                            "[Acceptance]\n"
                            "REQ-001: status=satisfied; source=user; owner=main; "
                            f"verification=tests; evidence={evidence}\n\n"
                        ),
                    ).replace(
                        "[Gates]\n\n",
                        f"[Gates]\ngate-test: status=passed; kind=test; evidence={evidence}\n\n",
                    )
                )

                self.assertTrue(task_file.has_unresolved_acceptance)
                self.assertTrue(task_file.has_unresolved_gates)

    def test_duplicate_acceptance_and_gate_ids_block_finalization(self) -> None:
        task_file = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Acceptance]\n\n",
                (
                    "[Acceptance]\n"
                    "REQ-001: status=satisfied; source=user; owner=main; verification=tests; evidence=first\n"
                    "req-001: status=satisfied; source=user; owner=main; verification=tests; evidence=second\n\n"
                ),
            ).replace(
                "[Gates]\n\n",
                (
                    "[Gates]\n"
                    "gate-e2e-api: status=open; kind=e2e; evidence=pending\n"
                    "GATE-E2E-API: status=passed; kind=e2e; evidence=tests\n\n"
                ),
            )
        )

        self.assertFalse(task_file.is_finalized)
        self.assertIn(
            "acceptance-duplicate:req-001: status=satisfied; source=user; owner=main; verification=tests; evidence=second",
            task_file.finalization_blockers,
        )
        self.assertIn(
            "gate-duplicate:GATE-E2E-API: status=passed; kind=e2e; evidence=tests",
            task_file.finalization_blockers,
        )
        self.assertIn(
            "gate:gate-e2e-api: status=open; kind=e2e; evidence=pending",
            task_file.finalization_blockers,
        )

    def test_duplicate_sections_are_rejected_before_finalization(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate shared task file section 'Gates'"):
            SharedTaskFile.parse(DEFAULT_TASK_FILE + "\n[Gates]\ngate-test: status=passed; kind=test; evidence=tests\n")

    def test_malformed_gate_line_blocks_finalization(self) -> None:
        task_file = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Gates]\n\n",
                "[Gates]\nmalformed-gate-without-fields\n\n",
            )
        )

        self.assertFalse(task_file.is_finalized)
        self.assertIn("gate:malformed-gate-without-fields", task_file.finalization_blockers)

    def test_passed_visual_gate_requires_structured_ui_evidence(self) -> None:
        missing_details = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Gates]\n\n",
                "[Gates]\ngate-visual: status=passed; kind=visual; evidence=screenshot=desktop.png\n\n",
            )
        )
        complete_desktop = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Gates]\n\n",
                (
                    "[Gates]\n"
                    "gate-visual: status=passed; kind=visual; "
                    "evidence=url=http://localhost:3000 screenshot=desktop.png "
                    "viewport=1440x900 viewport_actual=1440x900 "
                    "console=none network=none agent=qa-ui "
                    "server_manifest=env/server-processes.json assertions=dom-contract.json "
                    "artifact_dir=artifacts/fit-check fit=no-overlap-no-clipping-no-horizontal-scroll "
                    "cleanup=server-stopped\n\n"
                ),
            )
        )
        mismatched_viewport = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Gates]\n\n",
                (
                    "[Gates]\n"
                    "gate-visual: status=passed; kind=visual; "
                    "evidence=url=http://localhost:3000 screenshot=desktop.png "
                    "viewport=1440x900 viewport_actual=390x844 "
                    "console=none network=none agent=qa-ui "
                    "server_manifest=env/server-processes.json assertions=dom-contract.json "
                    "artifact_dir=artifacts/fit-check fit=no-overlap-no-clipping-no-horizontal-scroll "
                    "cleanup=server-stopped\n\n"
                ),
            )
        )

        self.assertTrue(missing_details.has_unresolved_gates)
        self.assertIn("gate:gate-visual: status=passed; kind=visual; evidence=screenshot=desktop.png", missing_details.finalization_blockers)
        self.assertFalse(complete_desktop.has_unresolved_gates)
        self.assertTrue(mismatched_viewport.has_unresolved_gates)
        self.assertIn("viewport_actual=390x844", mismatched_viewport.finalization_blockers[0])

    def test_stop_hook_wake_reason_names_acceptance_and_gate_blockers(self) -> None:
        agent_state = AgentState.from_mapping(
            {"agent_kind": "main", "state": "done"}, default_agent_id="main"
        )
        acceptance = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Acceptance]\n\n",
                "[Acceptance]\nREQ-001: status=open; source=user; owner=main; verification=ui; evidence=pending\n\n",
            )
        )
        gates = SharedTaskFile.parse(
            DEFAULT_TASK_FILE.replace(
                "[Gates]\n\n",
                "[Gates]\ngate-visual: status=failed; kind=visual; evidence=shot.png\n\n",
            )
        )

        self.assertEqual(decide_wake(acceptance, agent_state).reason, "main_done_with_unresolved_acceptance")
        self.assertEqual(decide_wake(gates, agent_state).reason, "main_done_with_unresolved_gates")


if __name__ == "__main__":
    unittest.main()
