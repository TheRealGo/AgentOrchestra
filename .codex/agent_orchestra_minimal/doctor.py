from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .agent_state_doctor import finalized_task_file_agent_state_blockers
from .autonomy_policy import autonomy_policy_diagnostic_lines
from .codex_config import inspect_mcp_inheritance, mcp_command_by_server
from .codex_features import run_codex_features_list
from .doctor_codex import run_codex_doctor, summarize_codex_doctor
from .prepare_agent_launch import run_probe
from .server_process_runtime import alive, read_manifest
from .task_file import SharedTaskFile
from .tmux_liveness import inspect_pane_liveness


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
    if "TMUX" not in os.environ and args.tui_transport:
        failures.append("not running inside tmux for --tui-transport")

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
    if getattr(args, "codex_features", False):
        report = run_codex_features_list()
        if report.failed:
            print("agent-orchestra doctor: failed", file=sys.stderr)
            for line in report.lines:
                print(f"- {line}", file=sys.stderr)
            return 1
        for line in report.lines:
            print(f"agent-orchestra doctor: {line}", file=sys.stderr)
    if getattr(args, "mcp", False):
        report = inspect_mcp(command_checker=command_available)
        if report.failed:
            print("agent-orchestra doctor: failed", file=sys.stderr)
            for line in report.lines:
                print(f"- {line}", file=sys.stderr)
            return 1
        for line in report.lines:
            print(f"agent-orchestra doctor: {line}", file=sys.stderr)
    if task_file_path := getattr(args, "task_file", None):
        report = inspect_task_file(Path(task_file_path).expanduser())
        if report.failed:
            print("agent-orchestra doctor: failed", file=sys.stderr)
            for line in report.lines:
                print(f"- {line}", file=sys.stderr)
            return 1
        for line in report.lines:
            print(f"agent-orchestra doctor: {line}", file=sys.stderr)
    if getattr(args, "server_processes", False):
        report = inspect_server_processes(Path(args.server_process_root).expanduser())
        if report.failed:
            print("agent-orchestra doctor: failed", file=sys.stderr)
            for line in report.lines:
                print(f"- {line}", file=sys.stderr)
            return 1
        for line in report.lines:
            print(f"agent-orchestra doctor: {line}", file=sys.stderr)
    if getattr(args, "autonomy_policy", False):
        for line in autonomy_policy_diagnostic_lines():
            print(f"agent-orchestra doctor: {line}", file=sys.stderr)
    if tmux_liveness_pane := getattr(args, "tmux_liveness_pane", None):
        report = inspect_tmux_liveness(
            tmux_liveness_pane,
            samples=args.tmux_liveness_samples,
            interval_seconds=args.tmux_liveness_interval_seconds,
        )
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


class TaskFileDoctorReport:
    def __init__(self, *, failed: bool, lines: list[str]) -> None:
        self.failed = failed
        self.lines = lines


class McpDoctorReport:
    def __init__(self, *, failed: bool, lines: list[str]) -> None:
        self.failed = failed
        self.lines = lines


class ServerProcessDoctorReport:
    def __init__(self, *, failed: bool, lines: list[str]) -> None:
        self.failed = failed
        self.lines = lines


class TmuxLivenessDoctorReport:
    def __init__(self, *, failed: bool, lines: list[str]) -> None:
        self.failed = failed
        self.lines = lines


def inspect_task_file(path: Path) -> TaskFileDoctorReport:
    try:
        task_file = SharedTaskFile.read(path)
    except (OSError, ValueError) as exc:
        return TaskFileDoctorReport(failed=True, lines=[f"shared task file invalid or unreadable: {path}: {exc}"])
    blockers = list(task_file.finalization_blockers)
    if task_file.is_finalized:
        blockers.extend(finalized_task_file_agent_state_blockers(path))
    if blockers:
        lines = ["shared task file has finalization blockers:"] + [f"  {blocker}" for blocker in blockers]
        return TaskFileDoctorReport(failed=True, lines=lines)
    return TaskFileDoctorReport(failed=False, lines=[f"shared task file finalized: {path}"])


def inspect_mcp(*, command_checker: Any = command_available) -> McpDoctorReport:
    inheritance = inspect_mcp_inheritance()
    if not inheritance.enabled:
        return McpDoctorReport(False, ["MCP inheritance disabled by environment"])
    if inheritance.error:
        return McpDoctorReport(True, [f"MCP config invalid: {inheritance.source_config}: {inheritance.error}"])
    source = str(inheritance.source_config) if inheritance.source_config else "not found"
    servers = ", ".join(inheritance.servers) if inheritance.servers else "(none)"
    lines = [
        f"MCP source config: {source}",
        f"MCP servers: {servers}",
        f"Playwright MCP: {'present' if inheritance.playwright_present else 'absent'}",
    ]
    failed = False
    commands = mcp_command_by_server(inheritance.source_config)
    for server in inheritance.servers:
        command = commands.get(server, "")
        if not command:
            continue
        name = Path(command).name
        available = command_checker(command)
        failed = failed or not available
        lines.append(f"MCP command {server}: {name} {'available' if available else 'missing'}")
    return McpDoctorReport(failed=failed, lines=lines)


def inspect_server_processes(root: Path, *, alive_checker: Any = alive) -> ServerProcessDoctorReport:
    if not root.exists():
        return ServerProcessDoctorReport(False, [f"server process root not found: {root}"])
    if not root.is_dir():
        return ServerProcessDoctorReport(True, [f"server process root is not a directory: {root}"])

    live_entries: list[str] = []
    unreadable: list[str] = []
    manifests = sorted(root.glob("**/server-processes.json"))
    for manifest in manifests:
        try:
            data = read_manifest(manifest)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            unreadable.append(f"{manifest}: {exc}")
            continue
        for name, server_entry in sorted(data.items()):
            if not isinstance(server_entry, dict):
                continue
            if server_entry.get("status") not in {"running", "starting"}:
                continue
            pid = int(server_entry.get("pid") or 0)
            if pid <= 0 or not alive_checker(pid):
                continue
            base_url = str(server_entry.get("base_url") or "")
            owner = str(server_entry.get("owner_agent_id") or "unknown")
            cleanup = "recorded" if server_entry.get("cleanup_command") else "missing"
            live_entries.append(
                f"{manifest}: {name} status={server_entry.get('status')} pid={pid} "
                f"base_url={base_url} owner={owner} cleanup={cleanup}"
            )

    lines = [f"server process manifests scanned: {len(manifests)} under {root}"]
    if unreadable:
        lines.append("unreadable server process manifests:")
        lines.extend(f"  {item}" for item in unreadable)
    if live_entries:
        lines.append("live server processes remain:")
        lines.extend(f"  {item}" for item in live_entries)
    if len(lines) == 1:
        lines.append("no live server processes recorded")
    return ServerProcessDoctorReport(failed=bool(unreadable or live_entries), lines=lines)


def inspect_tmux_liveness(
    pane_target: str,
    *,
    samples: int,
    interval_seconds: float,
) -> TmuxLivenessDoctorReport:
    try:
        liveness = inspect_pane_liveness(
            pane_target,
            samples=samples,
            interval_seconds=interval_seconds,
        )
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        return TmuxLivenessDoctorReport(
            failed=True,
            lines=[f"tmux pane liveness check failed for {pane_target}: {exc}"],
        )
    lines = [
        f"tmux pane {pane_target} state={liveness.state} changed={str(liveness.changed).lower()}",
        f"tmux pane reason: {liveness.reason}",
    ]
    if liveness.stale_working:
        lines.append("tmux pane stale Working requires interrupt, recovery, blocker, or relaunch evidence")
    return TmuxLivenessDoctorReport(failed=liveness.stale_working, lines=lines)
