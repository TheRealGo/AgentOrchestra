from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal import self_e2e_finalizer  # noqa: E402
from agent_orchestra_minimal.self_exit import SelfExitResult  # noqa: E402
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402
from self_e2e_status_helpers import SELF_E2E_FINALIZED_TASK_FILE  # noqa: E402


class SelfE2EFinalizerTests(unittest.TestCase):
    def test_cli_writes_result_then_finalizes_status_done_with_space_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            tmp = Path(tmpdir)
            task_file, status_file, result_file = self._paths(tmp)
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")

            with self._patched_self_exit():
                rc = self_e2e_finalizer.main(
                    [
                        "--pane",
                        "%439",
                        "--foreground",
                        "--task-file",
                        str(task_file),
                        "--status-path",
                        str(status_file),
                        "--result-path",
                        str(result_file),
                        "--cleanup-auxiliary-shells",
                        "--delay-seconds",
                        "0",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertTrue(result_file.is_file())
            self.assertEqual(
                json.loads(
                    (status_file.parent / "active-main-session.json").read_text(
                        encoding="utf-8"
                    )
                ),
                {
                    "pane": "%439",
                    "session_name": "AgentOrchestra-self-e2e-20260621-200315",
                },
            )
            self.assertEqual(
                json.loads(result_file.read_text(encoding="utf-8")),
                {
                    "attempts": 1,
                    "auxiliary_shell_panes": ["%440", "%441"],
                    "cleared_leftover": False,
                    "closed": True,
                    "killed_pane": False,
                    "pane": "%439",
                    "reason": "pane_closed",
                    "session_gone": True,
                    "session_name": "AgentOrchestra-self-e2e-20260621-200315",
                },
            )
            self.assertEqual(status_file.read_text(encoding="utf-8"), "done")

    def test_cli_keeps_status_progress_when_task_readback_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            tmp = Path(tmpdir)
            task_file, status_file, result_file = self._paths(tmp)
            task_file.write_text(
                DEFAULT_TASK_FILE.replace("[status]\ndone", "[status]\nprogress"),
                encoding="utf-8",
            )

            with self._patched_self_exit():
                rc = self_e2e_finalizer.main(
                    [
                        "--pane",
                        "%439",
                        "--foreground",
                        "--task-file",
                        str(task_file),
                        "--status-path",
                        str(status_file),
                        "--result-path",
                        str(result_file),
                        "--delay-seconds",
                        "0",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertTrue(result_file.is_file())
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")

    def test_cli_keeps_status_progress_when_session_gone_is_not_true(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            tmp = Path(tmpdir)
            task_file, status_file, result_file = self._paths(tmp)
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")

            with self._patched_self_exit(session_gone=False):
                rc = self_e2e_finalizer.main(
                    [
                        "--pane",
                        "%439",
                        "--foreground",
                        "--task-file",
                        str(task_file),
                        "--status-path",
                        str(status_file),
                        "--result-path",
                        str(result_file),
                        "--cleanup-auxiliary-shells",
                        "--delay-seconds",
                        "0",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")
            self.assertEqual(
                json.loads(result_file.read_text(encoding="utf-8"))["session_gone"],
                False,
            )

    def test_cli_validates_current_result_path_not_newer_stale_self_exit_json(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            tmp = Path(tmpdir)
            task_file, status_file, result_file = self._paths(tmp)
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            stale_result = status_file.parent / "main-self-exit-stale.json"
            stale_result.parent.mkdir(parents=True)
            stale_result.write_text(
                json.dumps(
                    {
                        "attempts": 1,
                        "auxiliary_shell_panes": ["%440", "%441"],
                        "cleared_leftover": False,
                        "closed": True,
                        "killed_pane": False,
                        "pane": "%439",
                        "reason": "pane_closed",
                        "session_gone": True,
                        "session_name": "AgentOrchestra-self-e2e-20260621-200315",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            os.utime(stale_result, (4102444800, 4102444800))

            with self._patched_self_exit(session_gone=False):
                rc = self_e2e_finalizer.main(
                    [
                        "--pane",
                        "%439",
                        "--foreground",
                        "--task-file",
                        str(task_file),
                        "--status-path",
                        str(status_file),
                        "--result-path",
                        str(result_file),
                        "--cleanup-auxiliary-shells",
                        "--delay-seconds",
                        "0",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertEqual(status_file.read_text(encoding="utf-8"), "progress")
            self.assertFalse(json.loads(result_file.read_text(encoding="utf-8"))["session_gone"])

    def test_finalizer_rejects_non_self_e2e_session_before_self_exit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            tmp = Path(tmpdir)
            task_file, status_file, result_file = self._paths(tmp)
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")

            with self._patched_self_exit(session_name="ToO"):
                with self.assertRaisesRegex(ValueError, "dedicated"):
                    self_e2e_finalizer.run_finalize_after_self_exit(
                        pane="%439",
                        task_file_path=task_file,
                        status_path=status_file,
                        result_path=result_file,
                        submit_key="C-m",
                        delay_seconds=0,
                    )

            self.assertFalse(result_file.exists())

    def test_finalizer_rejects_active_main_binding_mismatch_before_self_exit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Application Support ") as tmpdir:
            tmp = Path(tmpdir)
            task_file, status_file, result_file = self._paths(tmp)
            task_file.write_text(SELF_E2E_FINALIZED_TASK_FILE, encoding="utf-8")
            status_file.parent.mkdir(parents=True)
            (status_file.parent / "active-main-session.json").write_text(
                json.dumps(
                    {
                        "pane": "%581",
                        "session_name": "AgentOrchestra-self-e2e-20260622-025415",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            with self._patched_self_exit(session_name="AgentOrchestra-self-e2e-20260622-030000"):
                with self.assertRaisesRegex(ValueError, "active-main-session"):
                    self_e2e_finalizer.run_finalize_after_self_exit(
                        pane="%439",
                        task_file_path=task_file,
                        status_path=status_file,
                        result_path=result_file,
                        submit_key="C-m",
                        delay_seconds=0,
                    )

            self.assertFalse(result_file.exists())

    def _paths(self, tmp: Path) -> tuple[Path, Path, Path]:
        task_file = tmp / "tasks.ini"
        status_file = tmp / ".tmp" / "self-improvement-e2e" / "status"
        result_file = status_file.parent / "main-self-exit.json"
        return task_file, status_file, result_file

    def _patched_self_exit(
        self,
        *,
        session_gone: bool = True,
        session_name: str = "AgentOrchestra-self-e2e-20260621-200315",
    ) -> "_Patch":
        return _Patch(session_gone=session_gone, session_name=session_name)


class _Patch:
    def __init__(
        self,
        *,
        session_gone: bool = True,
        session_name: str = "AgentOrchestra-self-e2e-20260621-200315",
    ) -> None:
        self.session_gone = session_gone
        self.session_name = session_name

    def __enter__(self) -> None:
        self.original_run_self_exit = self_e2e_finalizer.run_self_exit
        self.original_tmux_session_name = self_e2e_finalizer._tmux_session_name

        def fake_run_self_exit(*_: object, **__: object) -> SelfExitResult:
            return SelfExitResult(
                closed=True,
                attempts=1,
                cleared_leftover=False,
                killed_pane=False,
                reason="pane_closed",
                pane="%439",
                session_name=self.session_name,
                auxiliary_shell_panes=("%440", "%441"),
                session_gone=self.session_gone,
            )

        self_e2e_finalizer.run_self_exit = fake_run_self_exit  # type: ignore[assignment]
        self_e2e_finalizer._tmux_session_name = (  # type: ignore[assignment]
            lambda *_args, **_kwargs: self.session_name
        )

    def __exit__(self, *_: object) -> None:
        self_e2e_finalizer.run_self_exit = self.original_run_self_exit  # type: ignore[attr-defined]
        self_e2e_finalizer._tmux_session_name = self.original_tmux_session_name  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
