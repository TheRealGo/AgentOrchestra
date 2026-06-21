from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.self_exit import SelfExitResult  # noqa: E402
from agent_orchestra_minimal import self_exit_cli  # noqa: E402
from agent_orchestra_minimal.self_exit_cli import main  # noqa: E402


class SelfExitCliTests(unittest.TestCase):
    def test_cli_imports_under_package_context(self) -> None:
        self.assertTrue(callable(main))

    def test_cli_rejects_direct_selfe2e_main_self_exit_evidence_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            result_path = Path(tmp) / ".tmp" / "self-improvement-e2e" / "main-self-exit.json"

            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "--pane",
                        "%439",
                        "--foreground",
                        "--result-path",
                        str(result_path),
                        "--delay-seconds",
                        "0",
                    ]
                )

            self.assertEqual(rc, 2)
            self.assertIn("use agent_orchestra_minimal.self_e2e_finalizer", stderr.getvalue())
            self.assertFalse(result_path.exists())

    def test_cli_allows_non_selfe2e_result_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result_path = Path(tmp) / "self-exit-pro-layer15.json"
            original = self_exit_cli.self_exit_runtime.run_self_exit

            def fake_run_self_exit(*_: object, **__: object) -> SelfExitResult:
                return SelfExitResult(
                    closed=True,
                    attempts=1,
                    cleared_leftover=False,
                    killed_pane=False,
                    reason="pane_closed",
                    pane="%9",
                )

            try:
                self_exit_cli.self_exit_runtime.run_self_exit = fake_run_self_exit  # type: ignore[assignment]
                rc = main(
                    [
                        "--pane",
                        "%9",
                        "--foreground",
                        "--delay-seconds",
                        "0",
                        "--result-path",
                        str(result_path),
                    ]
                )
            finally:
                self_exit_cli.self_exit_runtime.run_self_exit = original  # type: ignore[assignment]

            self.assertEqual(rc, 0)
            self.assertTrue(result_path.is_file())


if __name__ == "__main__":
    unittest.main()
