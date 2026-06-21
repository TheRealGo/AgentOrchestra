from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.apply_back_readiness import (  # noqa: E402
    assert_no_run_local_evidence_references,
    find_run_local_evidence_references,
)


class ApplyBackReadinessTests(unittest.TestCase):
    def test_tracked_tests_must_not_reference_run_local_evidence_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests = root / "tests"
            tests.mkdir()
            run_local_path = ".tmp/self-improvement-e2e" + "/service-e2e-defect-brief.md"
            (tests / "test_bad.py").write_text(
                f'fixture = Path("{run_local_path}").read_text()\n',
                encoding="utf-8",
            )

            references = find_run_local_evidence_references(root)

            self.assertEqual(len(references), 1)
            self.assertEqual(references[0].path, Path("tests/test_bad.py"))
            with self.assertRaisesRegex(ValueError, "run-local evidence"):
                assert_no_run_local_evidence_references(root)

    def test_inline_fixtures_do_not_trigger_apply_back_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_good.py").write_text("fixture = 'observed defect text inline'\n", encoding="utf-8")

            self.assertEqual(find_run_local_evidence_references(root), [])
            assert_no_run_local_evidence_references(root)

    def test_current_repo_has_no_tracked_test_reads_from_run_local_evidence(self) -> None:
        self.assertEqual(find_run_local_evidence_references(ROOT), [])
        assert_no_run_local_evidence_references(ROOT)


if __name__ == "__main__":
    unittest.main()
