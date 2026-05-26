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
    if not codex_auth_available():
        failures.append("Codex auth.json was not found in CODEX_HOME or ~/.codex.")
    for command in ("codex", "tmux"):
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
        probe = run_probe(codex_binary="codex")
        if not probe.ok:
            print("agent-orchestra doctor: failed", file=sys.stderr)
            print(f"- TUI transport probe failed: {probe.message}", file=sys.stderr)
            if probe.capture_tail:
                print(probe.capture_tail, file=sys.stderr)
            return 1
    print("agent-orchestra doctor: ok")
    return 0


def codex_auth_available() -> bool:
    candidates: list[Path] = []
    if codex_home := os.environ.get("CODEX_HOME"):
        candidates.append(Path(codex_home).expanduser() / "auth.json")
    candidates.append(Path.home() / ".codex" / "auth.json")
    return any(path.is_file() for path in candidates)


def command_available(command: str) -> bool:
    return shutil.which(command) is not None
