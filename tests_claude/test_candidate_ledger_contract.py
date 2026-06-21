from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.task_file import SharedTaskFile  # noqa: E402


TASK_FILE = """\
[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]
{candidate}

[Done]
"""


class CandidateLedgerContractTests(unittest.TestCase):
    def test_completed_candidates_require_id_summary_and_evidence(self) -> None:
        candidates = (
            "disposition=integrated; summary=retry send; evidence=tests",
            "candidate-1: disposition=integrated; evidence=tests",
            "candidate-1: disposition=integrated; summary=retry send",
        )
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                task_file = SharedTaskFile.parse(TASK_FILE.format(candidate=candidate))

                self.assertTrue(task_file.has_unresolved_candidates)

    def test_completed_candidate_evidence_cannot_be_placeholder(self) -> None:
        for evidence in ("pending", "TBD", "todo", "unknown"):
            with self.subTest(evidence=evidence):
                task_file = SharedTaskFile.parse(
                    TASK_FILE.format(
                        candidate=(
                            "candidate-1: disposition=rejected; "
                            "summary=no remaining issue; "
                            f"evidence={evidence}"
                        )
                    )
                )

                self.assertTrue(task_file.has_unresolved_candidates)
                self.assertIn(
                    "candidate:candidate-1: disposition=rejected; "
                    f"summary=no remaining issue; evidence={evidence}",
                    task_file.finalization_blockers,
                )

    def test_completed_candidate_evidence_may_contain_colons(self) -> None:
        candidates = (
            "candidate-1: disposition=integrated; summary=retry send; evidence=tests/test.py:12",
            "candidate-1: disposition=integrated; summary=retry send; evidence=https://example.com/review",
            "candidate-1: disposition=integrated; summary=retry send; evidence=pane:%1153",
        )
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                task_file = SharedTaskFile.parse(TASK_FILE.format(candidate=candidate))

                self.assertFalse(task_file.has_unresolved_candidates)

    def test_candidates_with_duplicate_field_keys_remain_unresolved(self) -> None:
        candidates = (
            "candidate-1: disposition=integrated; disposition=deferred; summary=retry send; evidence=tests",
            "candidate-1: disposition=integrated; summary=retry send; summary=review retry; evidence=tests",
            "candidate-1: disposition=integrated; summary=retry send; evidence=tests; evidence=pane:%1153",
            "candidate-1: disposition=integrated; Summary=retry send; summary=review retry; evidence=tests",
            "candidate-1: disposition=integrated; summary=retry send; evidence=tests; Evidence=pane:%1153",
        )
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                task_file = SharedTaskFile.parse(TASK_FILE.format(candidate=candidate))

                self.assertTrue(task_file.has_unresolved_candidates)

    def test_candidate_field_keys_are_case_insensitive_for_required_evidence(self) -> None:
        task_file = SharedTaskFile.parse(
            TASK_FILE.format(
                candidate="candidate-1: Disposition=integrated; Summary=retry send; Evidence=tests"
            )
        )

        self.assertFalse(task_file.has_unresolved_candidates)

    def test_duplicate_candidate_ids_are_invalid(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate candidate id"):
            SharedTaskFile.parse(
                TASK_FILE.format(
                    candidate=(
                        "candidate-1: disposition=integrated; summary=retry send; evidence=tests\n"
                        "candidate-1: disposition=deferred; summary=retry send; evidence=review"
                    )
                )
            )

    def test_duplicate_candidate_ids_are_case_insensitive(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate candidate id"):
            SharedTaskFile.parse(
                TASK_FILE.format(
                    candidate=(
                        "Candidate-1: disposition=integrated; summary=retry send; evidence=tests\n"
                        "candidate-1: disposition=deferred; summary=retry send; evidence=review"
                    )
                )
            )

    def test_all_completed_dispositions_satisfy_finalization(self) -> None:
        dispositions = (
            "integrated",
            "rejected",
            "deferred",
            "blocked",
            "out-of-scope",
            "needs_user",
        )
        for disposition in dispositions:
            with self.subTest(disposition=disposition):
                task_file = SharedTaskFile.parse(
                    TASK_FILE.format(
                        candidate=(
                            "candidate-1: "
                            f"disposition={disposition}; "
                            "summary=reviewed residual; "
                            "evidence=Handoff.md"
                        )
                    )
                )

                self.assertTrue(task_file.is_finalized)
                self.assertEqual(task_file.finalization_blockers, [])

    def test_finalization_blockers_name_status_open_work_and_candidates(self) -> None:
        text = TASK_FILE.format(
            candidate="candidate-1: disposition=open; summary=missing release note; evidence=Handoff.md"
        ).replace("[status]\ndone", "[status]\nprogress")
        text = text.replace("[InReview]\n\n", "[InReview]\nreview-release-evidence\n\n")

        task_file = SharedTaskFile.parse(text)

        self.assertFalse(task_file.is_finalized)
        self.assertEqual(
            task_file.finalization_blockers,
            [
                "status=progress",
                "open:review-release-evidence",
                "candidate:candidate-1: disposition=open; summary=missing release note; evidence=Handoff.md",
            ],
        )


if __name__ == "__main__":
    unittest.main()
