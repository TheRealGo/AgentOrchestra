from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.prepare_agent_launch import run_probe  # noqa: E402


class ProbeCleanupTests(unittest.TestCase):
    def test_tui_probe_defaults_blank_submit_key(self) -> None:
        sent_keys: list[list[str]] = []

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            if args[:2] == ["tmux", "list-panes"]:
                # Claude Code pane identity is matched on pane_title containing
                # "Claude Code" from the tab-separated -F output.
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout="%1\tnode — Claude Code\t1\n", stderr=""
                )
            if args[:2] == ["tmux", "send-keys"]:
                sent_keys.append(args)
            if args[:2] == ["tmux", "has-session"]:
                return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="")
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        with patch("shutil.which", return_value="/bin/tool"), \
             patch("agent_orchestra_minimal.prepare_agent_launch._run", side_effect=fake_run), \
             patch("time.sleep", lambda *_a: None), \
             patch.dict("os.environ", {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "  "}, clear=False):
            result = run_probe(claude_binary="claude")

        self.assertTrue(result.ok)
        self.assertEqual(
            sent_keys,
            [
                ["tmux", "send-keys", "-t", "%1", "C-m"],
                ["tmux", "send-keys", "-t", "%1", "C-m"],
            ],
        )

    def test_tui_probe_rejects_invalid_submit_key_without_sending_keys(self) -> None:
        calls: list[list[str]] = []

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(args)
            return subprocess.CompletedProcess(
                args=args, returncode=0, stdout="%1\tnode — Claude Code\t1\n", stderr=""
            )

        with patch("shutil.which", return_value="/bin/tool"), \
             patch("agent_orchestra_minimal.prepare_agent_launch._run", side_effect=fake_run), \
             patch("time.sleep", lambda *_a: None), \
             patch.dict("os.environ", {"AGENT_ORCHESTRA_TUI_SUBMIT_KEY": "C-m Space"}, clear=False):
            result = run_probe(claude_binary="claude")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "submit_key must be a single tmux key token")
        self.assertFalse(any(args[:2] == ["tmux", "send-keys"] for args in calls))

    def test_tui_probe_removes_temp_root_after_start_failure(self) -> None:
        roots: list[Path] = []

        def fake_copy_auth(claude_config_dir: Path) -> None:
            roots.append(claude_config_dir.parent)
            claude_config_dir.mkdir(parents=True, exist_ok=True)
            (claude_config_dir / ".credentials.json").write_text('{"token":"redacted"}\n', encoding="utf-8")

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            if args[:3] == ["tmux", "new-session", "-d"]:
                return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="start failed")
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        with patch("shutil.which", return_value="/bin/tool"), \
             patch("agent_orchestra_minimal.prepare_agent_launch._copy_auth", side_effect=fake_copy_auth), \
             patch("time.sleep", lambda *_a: None), \
             patch("agent_orchestra_minimal.prepare_agent_launch._run", side_effect=fake_run):
            result = run_probe(claude_binary="claude")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "start failed")
        self.assertEqual(len(roots), 1)
        self.assertFalse(roots[0].exists())


if __name__ == "__main__":
    unittest.main()
