from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_CODE_FILE_LINES = 300
CODE_FILE_DIRS = (
    ROOT / ".codex" / "agent_orchestra_minimal",
    ROOT / ".codex" / "hooks",
    ROOT / "tests",
)


class RuntimeFileSizeContractTests(unittest.TestCase):
    def test_code_files_stay_below_spec_hard_limit(self) -> None:
        oversized_files = []
        for code_dir in CODE_FILE_DIRS:
            for path in sorted(code_dir.rglob("*.py")):
                line_count = len(path.read_text(encoding="utf-8").splitlines())
                if line_count > MAX_CODE_FILE_LINES:
                    oversized_files.append(
                        f"{path.relative_to(ROOT)} has {line_count} lines"
                    )

        self.assertEqual(
            oversized_files,
            [],
            "SPEC.md sets a hard 300-line limit for focused code files.",
        )


if __name__ == "__main__":
    unittest.main()
