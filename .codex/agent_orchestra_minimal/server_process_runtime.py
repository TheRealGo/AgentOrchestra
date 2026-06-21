from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .server_health import command_preview, log_tail


def entry(
    *,
    args: argparse.Namespace,
    cwd: Path,
    log_path: Path,
    stop_file: Path | None,
    pid: int | None,
    pgid: int | None,
    status: str,
) -> dict[str, Any]:
    cmd = list(args.cmd)
    if cmd[:1] == ["--"]:
        cmd = cmd[1:]
    result = {
        "name": args.name,
        "pid": pid,
        "pgid": pgid,
        "supervisor_pid": pid,
        "owner_agent_id": os.environ.get("AGENT_ORCHESTRA_AGENT_ID", ""),
        "owner_tmux_pane": os.environ.get("AGENT_ORCHESTRA_TMUX_PANE", ""),
        "cwd": str(cwd),
        "base_url": args.base_url,
        "port": args.port,
        "log_path": str(log_path),
        "stop_file": str(stop_file) if stop_file is not None else "",
        "cleanup_command": _cleanup_command(args),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command_preview": command_preview(cmd),
        "status": status,
    }
    health_url = getattr(args, "health_url", None)
    if health_url:
        result["health_url"] = health_url
        result["health_contains"] = getattr(args, "health_contains", None)
    return result


def _cleanup_command(args: argparse.Namespace) -> str:
    return (
        f"{shlex.quote(sys.executable)} -m agent_orchestra_minimal.server_process stop "
        f"--manifest {shlex.quote(str(args.manifest))} --name {shlex.quote(str(args.name))}"
    )


def startup_failure_entry(
    *,
    args: argparse.Namespace,
    cwd: Path,
    log_path: Path,
    failure: str,
    exit_code: int | None = None,
    health: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = entry(
        args=args,
        cwd=cwd,
        log_path=log_path,
        stop_file=None,
        pid=None,
        pgid=None,
        status="startup-failed",
    )
    result["startup_failure"] = failure
    result["exit_code"] = exit_code
    result["log_tail"] = log_tail(log_path)
    if health is not None and getattr(args, "health_url", None):
        result["health_url"] = args.health_url
        result["health_contains"] = getattr(args, "health_contains", None)
        result["health_error"] = health.get("error", "")
    return result


def request_supervised_stop(entry: dict[str, Any], pid: int, timeout: float) -> bool:
    stop_file_value = entry.get("stop_file")
    if not isinstance(stop_file_value, str) or not stop_file_value:
        return False
    stop_file = Path(stop_file_value)
    try:
        stop_file.parent.mkdir(parents=True, exist_ok=True)
        stop_file.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n", encoding="utf-8")
        stop_file.chmod(0o600)
    except OSError as exc:
        print(f"failed to request supervised stop: {exc}", file=sys.stderr)
        return False

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if reaped(pid) or not alive(pid):
            return True
        time.sleep(0.2)
    return reaped(pid) or not alive(pid)


def terminate_group(pgid: int, pid: int, timeout: float) -> bool:
    targets: list[tuple[str, int]] = []
    if pgid > 0:
        targets.append((f"process group {pgid}", -pgid))
    if pid > 0:
        targets.append((f"process {pid}", pid))
    for label, target in targets:
        if _terminate_target(label, target, pid, timeout):
            return True
    return False


def pgid(pid: int) -> int:
    try:
        return os.getpgid(pid)
    except OSError:
        return pid


def read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def write_manifest(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def reaped(pid: int) -> bool:
    try:
        result, _status = os.waitpid(pid, os.WNOHANG)
    except ChildProcessError:
        return False
    except OSError:
        return False
    return result == pid


def alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def wait_child_or_terminate(child: subprocess.Popen[Any]) -> int:
    try:
        return int(child.wait(timeout=10.0) or 0)
    except subprocess.TimeoutExpired:
        terminate_group(pgid(child.pid), child.pid, 2.0)
        return int(child.poll() or 1)


def _terminate_target(label: str, target: int, pid: int, timeout: float) -> bool:
    try:
        os.kill(target, signal.SIGTERM)
    except ProcessLookupError:
        return True
    except PermissionError as exc:
        print(f"failed to stop {label}: {exc}", file=sys.stderr)
        return False

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if reaped(pid) or not alive(pid):
            return True
        time.sleep(0.2)
    try:
        os.kill(target, signal.SIGKILL)
    except ProcessLookupError:
        return True
    except PermissionError as exc:
        print(f"failed to kill {label}: {exc}", file=sys.stderr)
        return False
    return reaped(pid) or not alive(pid)
