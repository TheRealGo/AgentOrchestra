from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.prepare_agent_launch import run_probe  # noqa: E402


class ProbeCleanupTests(unittest.TestCase):
    def test_tui_probe_defaults_blank_submit_key(self) -> None:
        sent_keys: list[list[str]] = []
        launch_commands: list[str] = []

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            if args[:3] == ["tmux", "new-session", "-d"]:
                launch_commands.append(args[-1])
            if args[:2] == ["tmux", "list-panes"]:
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="%1 node 1\n", stderr="")
            if args[:2] == ["tmux", "send-keys"]:
                sent_keys.append(args)
            if args[:2] == ["tmux", "has-session"]:
                return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="")
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        with patch("shutil.which", return_value="/bin/tool"), \
             patch("agent_orchestra_minimal.prepare_agent_launch._run", side_effect=fake_run), \
             patch.dict("os.environ", {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "  "}, clear=False):
            result = run_probe(codex_binary="codex")

        self.assertTrue(result.ok)
        self.assertEqual(len(launch_commands), 1)
        self.assertIn("--profile agent-orchestra", launch_commands[0])
        self.assertEqual(
            sent_keys,
            [
                ["tmux", "send-keys", "-t", "%1", "/exit", "C-m"],
            ],
        )

    def test_tui_probe_retries_submit_key_when_exit_stays_queued(self) -> None:
        sent_keys: list[list[str]] = []
        has_session_checks = 0

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            nonlocal has_session_checks
            if args[:2] == ["tmux", "list-panes"]:
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="%1 node 1\n", stderr="")
            if args[:2] == ["tmux", "send-keys"]:
                sent_keys.append(args)
            if args[:2] == ["tmux", "has-session"]:
                has_session_checks += 1
                returncode = 1 if has_session_checks == 6 else 0
                return subprocess.CompletedProcess(args=args, returncode=returncode, stdout="", stderr="")
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        with patch("time.sleep", return_value=None), \
             patch("shutil.which", return_value="/bin/tool"), \
             patch("agent_orchestra_minimal.prepare_agent_launch._run", side_effect=fake_run), \
             patch.dict("os.environ", {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": ""}, clear=False):
            result = run_probe(codex_binary="codex")

        self.assertTrue(result.ok)
        self.assertEqual(
            sent_keys,
            [
                ["tmux", "send-keys", "-t", "%1", "/exit", "C-m"],
                ["tmux", "send-keys", "-t", "%1", "C-m"],
            ],
        )

    def test_tui_probe_rejects_invalid_submit_key_without_sending_keys(self) -> None:
        calls: list[list[str]] = []

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(args)
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="%1 node 1\n", stderr="")

        with patch("shutil.which", return_value="/bin/tool"), \
             patch("agent_orchestra_minimal.prepare_agent_launch._run", side_effect=fake_run), \
             patch.dict("os.environ", {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "C-m Space"}, clear=False):
            result = run_probe(codex_binary="codex")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "submit_key must be a single tmux key token")
        self.assertFalse(any(args[:2] == ["tmux", "send-keys"] for args in calls))

    def test_tui_probe_removes_temp_root_after_start_failure(self) -> None:
        roots: list[Path] = []

        def fake_copy_auth(codex_home: Path) -> None:
            roots.append(codex_home.parent)
            codex_home.mkdir(parents=True, exist_ok=True)
            (codex_home / "auth.json").write_text('{"token":"redacted"}\n', encoding="utf-8")

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            if args[:3] == ["tmux", "new-session", "-d"]:
                return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="start failed")
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        with patch("shutil.which", return_value="/bin/tool"), \
             patch("agent_orchestra_minimal.prepare_agent_launch._copy_auth", side_effect=fake_copy_auth), \
             patch("agent_orchestra_minimal.prepare_agent_launch._run", side_effect=fake_run):
            result = run_probe(codex_binary="codex")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "start failed")
        self.assertEqual(len(roots), 1)
        self.assertFalse(roots[0].exists())


if __name__ == "__main__":
    unittest.main()
