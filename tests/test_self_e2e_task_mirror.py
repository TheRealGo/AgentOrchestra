from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.self_e2e_status import SelfE2EStatusResult  # noqa: E402
from agent_orchestra_minimal.self_e2e_task_mirror import (  # noqa: E402
    mirror_self_e2e_blockers_to_task_file,
)
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE, SharedTaskFile  # noqa: E402


class SelfE2ETaskMirrorTests(unittest.TestCase):
    def test_mirrors_missing_selfe2e_depth_blockers_back_to_done_task_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            task_file.write_text(DEFAULT_TASK_FILE, encoding="utf-8")

            mirror_self_e2e_blockers_to_task_file(
                task_file_path=task_file,
                status=SelfE2EStatusResult(
                    status="progress",
                    observed="progress",
                    task_finalized=False,
                    blockers=("self-e2e-missing:service-approval-replay",),
                ),
            )

            parsed = SharedTaskFile.read(task_file)
            self.assertEqual(parsed.status, "progress")
            self.assertTrue(parsed.has_unresolved_candidates)
            self.assertTrue(
                any(
                    item.startswith("selfe2e-finalizer-self-e2e-missing-service-approval-replay:")
                    for item in parsed.sections["Candidates"]
                )
            )

    def test_leaves_already_progress_task_file_unchanged(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            task_file = Path(tmpdir) / "tasks.ini"
            original = DEFAULT_TASK_FILE.replace("[status]\ndone", "[status]\nprogress")
            task_file.write_text(original, encoding="utf-8")

            mirror_self_e2e_blockers_to_task_file(
                task_file_path=task_file,
                status=SelfE2EStatusResult(
                    status="progress",
                    observed="progress",
                    task_finalized=False,
                    blockers=("status=progress",),
                ),
            )

            self.assertEqual(task_file.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
