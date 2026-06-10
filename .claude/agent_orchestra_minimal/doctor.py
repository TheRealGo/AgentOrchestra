from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from .prepare_agent_launch import run_probe


def doctor_command(args: argparse.Namespace) -> int:
    target = Path(args.target_project).expanduser().resolve()
    failures: list[str] = []
    if not target.is_dir():
        failures.append(f"target project is not a directory: {target}")
    if not claude_auth_available():
        failures.append(
            "Claude Code auth was not found (no .credentials.json, no API key env, and not on macOS Keychain)."
        )
    for command in ("claude", "tmux"):
        if not command_available(command):
            failures.append(f"required command is not available on PATH: {command}")
    if "TMUX" not in os.environ and not args.tui_transport:
        failures.append("not running inside tmux")

    if failures:
        print("agent-orchestra doctor: failed", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    if args.tui_transport:
        probe = run_probe(claude_binary="claude")
        if not probe.ok:
            print("agent-orchestra doctor: failed", file=sys.stderr)
            print(f"- TUI transport probe failed: {probe.message}", file=sys.stderr)
            if probe.capture_tail:
                print(probe.capture_tail, file=sys.stderr)
            return 1
    print("agent-orchestra doctor: ok")
    return 0


def claude_auth_available() -> bool:
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return True
    candidates: list[Path] = []
    if config_dir := os.environ.get("CLAUDE_CONFIG_DIR"):
        candidates.append(Path(config_dir).expanduser() / ".credentials.json")
    candidates.append(Path.home() / ".claude" / ".credentials.json")
    if any(path.is_file() for path in candidates):
        return True
    # On macOS, Claude Code reads credentials from the system Keychain, so a
    # missing credentials file does not mean the user is unauthenticated.
    return sys.platform == "darwin"


def command_available(command: str) -> bool:
    return shutil.which(command) is not None
