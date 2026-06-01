from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

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
    if getattr(args, "codex_doctor", False):
        report = run_codex_doctor(timeout_seconds=args.codex_doctor_timeout_seconds)
        if report.failed:
            print("agent-orchestra doctor: failed", file=sys.stderr)
            for line in report.lines:
                print(f"- {line}", file=sys.stderr)
            return 1
        for line in report.lines:
            print(f"agent-orchestra doctor: {line}", file=sys.stderr)
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


class CodexDoctorReport:
    def __init__(self, *, failed: bool, lines: list[str]) -> None:
        self.failed = failed
        self.lines = lines


def run_codex_doctor(
    *,
    timeout_seconds: float,
    runner: Any = subprocess.run,
) -> CodexDoctorReport:
    try:
        result = runner(
            ["codex", "doctor", "--json"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return CodexDoctorReport(
            failed=True,
            lines=[f"Codex doctor timed out after {timeout_seconds:g}s"],
        )
    except OSError as exc:
        return CodexDoctorReport(
            failed=True,
            lines=[f"Codex doctor could not run: {exc}"],
        )

    stdout = result.stdout.strip()
    if not stdout:
        stderr = result.stderr.strip()
        detail = f": {stderr}" if stderr else ""
        return CodexDoctorReport(
            failed=True,
            lines=[f"Codex doctor returned no JSON output{detail}"],
        )
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return CodexDoctorReport(
            failed=True,
            lines=[f"Codex doctor returned invalid JSON: {exc.msg}"],
        )
    if not isinstance(payload, dict):
        return CodexDoctorReport(
            failed=True,
            lines=[f"Codex doctor returned JSON {type(payload).__name__}, expected object"],
        )
    return summarize_codex_doctor(payload, returncode=result.returncode)


def summarize_codex_doctor(payload: dict[str, Any], *, returncode: int) -> CodexDoctorReport:
    status = str(payload.get("overallStatus", "unknown"))
    version = str(payload.get("codexVersion", "unknown"))
    failed = status == "fail" or returncode != 0
    lines = [f"Codex doctor overallStatus={status} version={version}"]

    checks = payload.get("checks", {})
    if isinstance(checks, dict):
        for check_id in sorted(checks):
            check = checks[check_id]
            if not isinstance(check, dict):
                continue
            check_status = str(check.get("status", "unknown"))
            if check_status in {"ok", "idle"}:
                continue
            category = str(check.get("category", "unknown"))
            summary = str(check.get("summary", "")).strip()
            line = f"Codex doctor {check_status}: {category}/{check_id}"
            if summary:
                line = f"{line}: {summary}"
            remediation = str(check.get("remediation", "") or "").strip()
            if remediation:
                line = f"{line} ({remediation})"
            lines.append(line)

    if len(lines) == 1 and status == "ok":
        lines[0] = f"Codex doctor ok version={version}"
    return CodexDoctorReport(failed=failed, lines=lines)
