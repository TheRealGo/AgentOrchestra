from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReadmeVerificationContractTests(unittest.TestCase):
    def test_readmes_describe_team_task_state_and_delivery_contracts(self) -> None:
        required_by_readme = {
            "README.md": (
                "tmux panes for the AgentTeam",
                "send tasks through tmux",
                "collect peer review",
                "retire those panes",
                "runtime only provides deterministic rails for launch, tmux delivery",
                "open work in `[Backlog]`, `[InProgress]`, or `[InReview]`",
                "every `[Candidates]` ledger item has an id, summary, completed disposition, and evidence pointer",
                "marked `retired`, sent `/exit`, and their panes are verified or cleaned up",
            ),
            "README.ja.md": (
                "AgentTeam 用の tmux pane",
                "tmux 経由でタスクを送り",
                "peer review を集め",
                "pane を退役",
                "起動、tmux 配送、共有タスク状態、Stop Hook wake",
                "Agent は `[Backlog]`、`[InProgress]`、`[InReview]` に open work を記録",
                "`[Candidates]` ledger の各項目に id、summary、完了 disposition、evidence",
                "`retired` にし、`/exit` を送り、pane が閉じたことを確認または cleanup",
            ),
        }

        for relative_path, phrases in required_by_readme.items():
            with self.subTest(relative_path=relative_path):
                readme = (ROOT / relative_path).read_text(encoding="utf-8")
                readme_normalized = " ".join(readme.split())

                for phrase in phrases:
                    self.assertIn(phrase, readme_normalized)

    def test_readmes_name_unittest_as_standard_runner(self) -> None:
        for relative_path in ("README.md", "README.ja.md"):
            with self.subTest(relative_path=relative_path):
                readme = (ROOT / relative_path).read_text(encoding="utf-8")

                self.assertIn("python3 -m unittest discover -s tests", readme)
                self.assertIn(
                    "find .codex/agent_orchestra_minimal .codex/hooks tests \\\n"
                    "  -name '*.py' -print0 | xargs -0 python3 -m py_compile",
                    readme,
                )
                self.assertIn("git diff --check", readme)
                self.assertIn("nix flake check --no-build", readme)
                self.assertIn("nix build .#checks.x86_64-linux.source-contract", readme)
                self.assertRegex(
                    readme,
                    re.compile(r"nix\s+flake\s+check\s+--no-build\s+path:\$PWD"),
                )
                self.assertIn(
                    "nix build path:$PWD#checks.$system.source-contract",
                    readme,
                )
                self.assertIn("pytest", readme)
                self.assertIn("unittest", readme)


if __name__ == "__main__":
    unittest.main()
