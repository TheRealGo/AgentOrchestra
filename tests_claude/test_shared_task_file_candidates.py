from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.task_file import SharedTaskFile  # noqa: E402


CANONICAL_EMPTY_TASK_FILE = """\
[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]

[Done]
completed item
"""


class SharedTaskFileCandidateTests(unittest.TestCase):
    def test_candidates_are_unresolved_until_disposed(self) -> None:
        for disposition in ("", "open", "backlog", "typo"):
            with self.subTest(disposition=disposition):
                candidate = "candidate-1: summary=retry send"
                if disposition:
                    candidate += f"; disposition={disposition}"
                task_file = SharedTaskFile.parse(
                    CANONICAL_EMPTY_TASK_FILE.replace(
                        "[Candidates]\n\n",
                        f"[Candidates]\n{candidate}\n\n",
                    )
                )

                self.assertTrue(task_file.has_unresolved_candidates)

    def test_completed_candidate_dispositions_are_not_open_candidates(self) -> None:
        for disposition in ("integrated", "rejected", "deferred", "blocked", "out-of-scope", "needs_user"):
            with self.subTest(disposition=disposition):
                task_file = SharedTaskFile.parse(
                    CANONICAL_EMPTY_TASK_FILE.replace(
                        "[Candidates]\n\n",
                        f"[Candidates]\ncandidate-1: disposition={disposition}; summary=retry send; evidence=tests\n\n",
                    )
                )

                self.assertFalse(task_file.has_unresolved_candidates)


if __name__ == "__main__":
    unittest.main()
