from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from agent_orchestra_minimal.manifest_lock import manifest_lock
    from agent_orchestra_minimal.server_health import http_health_check, log_tail, tcp_listening, wait_for_startup
    from agent_orchestra_minimal.server_process_runtime import (
        entry,
        pgid,
        read_manifest,
        request_supervised_stop,
        startup_failure_entry,
        terminate_group,
        wait_child_or_terminate,
        write_manifest,
    )
else:
    from .manifest_lock import manifest_lock
    from .server_health import http_health_check, log_tail, tcp_listening, wait_for_startup
    from .server_process_runtime import (
        entry,
        pgid,
        read_manifest,
        request_supervised_stop,
        startup_failure_entry,
        terminate_group,
        wait_child_or_terminate,
        write_manifest,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="start and stop AgentOrchestra runtime server processes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="start a long-running process and record it in a manifest")
    start.add_argument("--manifest", default=_default_manifest())
    start.add_argument("--name", required=True)
    start.add_argument("--cwd", default=os.getcwd())
    start.add_argument("--base-url", required=True)
    start.add_argument("--port", type=int)
    start.add_argument("--health-url")
    start.add_argument("--health-contains")
    start.add_argument("--health-timeout", type=float, default=1.0)
    start.add_argument(
        "--allow-tcp-readiness",
        action="store_true",
        help="allow TCP-only readiness for non-HTTP helpers when equivalent identity evidence is recorded separately",
    )
    start.add_argument("--log", required=True)
    start.add_argument("--startup-timeout", type=float, default=3.0)
    start.add_argument("cmd", nargs=argparse.REMAINDER)

    stop = subparsers.add_parser("stop", help="stop a process recorded in a manifest")
    stop.add_argument("--manifest", default=_default_manifest())
    stop.add_argument("--name", required=True)
    stop.add_argument("--timeout", type=float, default=10.0)

    stop_all = subparsers.add_parser("stop-all", help="stop every running process recorded in a manifest")
    stop_all.add_argument("--manifest", default=_default_manifest())
    stop_all.add_argument("--timeout", type=float, default=10.0)

    status = subparsers.add_parser("status", help="print manifest entries")
    status.add_argument("--manifest", default=_default_manifest())

    supervised = subparsers.add_parser("run-supervised", help=argparse.SUPPRESS)
    supervised.add_argument("--stop-file", required=True)
    supervised.add_argument("--cwd", required=True)
    supervised.add_argument("--log", required=True)
    supervised.add_argument("cmd", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)
    if args.command == "start":
        return _start(args)
    if args.command == "stop":
        return _stop(args)
    if args.command == "stop-all":
        return _stop_all(args)
    if args.command == "status":
        print(json.dumps(read_manifest(Path(args.manifest)), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "run-supervised":
        return _run_supervised(args)
    return 2


def _default_manifest() -> str:
    env_dir = os.environ.get("AGENT_ORCHESTRA_ENV_DIR") or os.getcwd()
    return str(Path(env_dir) / "server-processes.json")


def _start(args: argparse.Namespace) -> int:
    cmd = list(args.cmd)
    if cmd[:1] == ["--"]:
        cmd = cmd[1:]
    if not cmd:
        print("server_process start requires a command after --", file=sys.stderr)
        return 2

    manifest_path = Path(args.manifest)
    log_path = Path(args.log)
    cwd = Path(args.cwd).expanduser().resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if args.port is not None and not args.health_url and not args.allow_tcp_readiness:
        manifest_entry = startup_failure_entry(args=args, cwd=cwd, log_path=log_path, failure="missing-health-url")
        with manifest_lock(manifest_path):
            data = read_manifest(manifest_path)
            data[args.name] = manifest_entry
            write_manifest(manifest_path, data)
        print(json.dumps(manifest_entry, ensure_ascii=False, sort_keys=True))
        return 2
    if args.port is not None and tcp_listening("127.0.0.1", args.port):
        health = (
            http_health_check(
                args.health_url,
                contains=args.health_contains,
                timeout=args.health_timeout,
            )
            if args.health_url
            else {"ok": False}
        )
        failure = "port-already-serving-health-url" if health.get("ok") else "port-already-listening"
        manifest_entry = startup_failure_entry(args=args, cwd=cwd, log_path=log_path, failure=failure, health=health)
        with manifest_lock(manifest_path):
            data = read_manifest(manifest_path)
            data[args.name] = manifest_entry
            write_manifest(manifest_path, data)
        print(json.dumps(manifest_entry, ensure_ascii=False, sort_keys=True))
        return 1
    stop_file = manifest_path.parent / f"{args.name}-{os.getpid()}-{time.monotonic_ns()}.stop"
    supervisor_cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "run-supervised",
        "--stop-file",
        str(stop_file),
        "--cwd",
        str(cwd),
        "--log",
        str(log_path),
        "--",
        *cmd,
    ]
    child_env = os.environ.copy()
    child_env["AGENT_ORCHESTRA_SERVER_NAME"] = args.name
    child_env["AGENT_ORCHESTRA_SERVER_BASE_URL"] = args.base_url
    if args.port is not None:
        child_env["AGENT_ORCHESTRA_SERVER_PORT"] = str(args.port)
    try:
        process = subprocess.Popen(
            supervisor_cmd,
            cwd=str(Path(__file__).resolve().parent),
            env=child_env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        stop_file.unlink(missing_ok=True)
        raise
    # This helper intentionally leaves the process running after the launcher
    # exits. Mark the Popen object detached so in-process tests do not emit a
    # ResourceWarning when the object is destroyed.
    process._child_created = False  # type: ignore[attr-defined]

    manifest_entry = entry(
        args=args,
        cwd=cwd,
        log_path=log_path,
        stop_file=stop_file,
        pid=process.pid,
        pgid=pgid(process.pid),
        status="starting",
    )
    startup = wait_for_startup(
        process,
        args.port,
        args.startup_timeout,
        log_path,
        health_url=args.health_url,
        health_contains=args.health_contains,
        health_timeout=args.health_timeout,
    )
    if startup["status"] != "running":
        if startup.get("exit_code") is None:
            stopped = request_supervised_stop(manifest_entry, process.pid, 2.0)
            if not stopped:
                terminate_group(pgid(process.pid), process.pid, 2.0)
            startup["exit_code"] = process.poll()
        manifest_entry.update(startup)
        manifest_entry["log_tail"] = log_tail(log_path)
    else:
        manifest_entry.update(startup)
    with manifest_lock(manifest_path):
        data = read_manifest(manifest_path)
        data[args.name] = manifest_entry
        write_manifest(manifest_path, data)
    print(json.dumps(manifest_entry, ensure_ascii=False, sort_keys=True))
    return 0 if manifest_entry["status"] == "running" else 1


def _stop(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    with manifest_lock(manifest_path):
        data = read_manifest(manifest_path)
        manifest_entry = data.get(args.name)
        if not isinstance(manifest_entry, dict):
            print(f"server process {args.name!r} is not recorded", file=sys.stderr)
            return 1
        pid = int(manifest_entry.get("pid") or 0)
        process_group = int(manifest_entry.get("pgid") or pid)
        stopped = request_supervised_stop(manifest_entry, pid, args.timeout)
        if not stopped:
            stopped = terminate_group(process_group, pid, args.timeout)
        manifest_entry["status"] = "stopped" if stopped else "stop-failed"
        manifest_entry["stopped_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        data[args.name] = manifest_entry
        write_manifest(manifest_path, data)
    print(json.dumps(manifest_entry, ensure_ascii=False, sort_keys=True))
    return 0 if stopped else 1


def _stop_all(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    with manifest_lock(manifest_path):
        data = read_manifest(manifest_path)
        if not data:
            print(json.dumps({}, ensure_ascii=False, sort_keys=True))
            return 0
        result: dict[str, dict] = {}
        overall_ok = True
        for name, manifest_entry in data.items():
            if not isinstance(manifest_entry, dict):
                continue
            if manifest_entry.get("status") not in {"running", "starting"}:
                result[name] = manifest_entry
                continue
            pid = int(manifest_entry.get("pid") or 0)
            process_group = int(manifest_entry.get("pgid") or pid)
            stopped = request_supervised_stop(manifest_entry, pid, args.timeout)
            if not stopped:
                stopped = terminate_group(process_group, pid, args.timeout)
            manifest_entry["status"] = "stopped" if stopped else "stop-failed"
            manifest_entry["stopped_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            data[name] = manifest_entry
            result[name] = manifest_entry
            overall_ok = overall_ok and stopped
        write_manifest(manifest_path, data)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if overall_ok else 1


def _run_supervised(args: argparse.Namespace) -> int:
    cmd = list(args.cmd)
    if cmd[:1] == ["--"]:
        cmd = cmd[1:]
    if not cmd:
        print("server_process run-supervised requires a command after --", file=sys.stderr)
        return 2

    stop_file = Path(args.stop_file)
    cwd = Path(args.cwd).expanduser().resolve()
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stop_file.unlink(missing_ok=True)
    with log_path.open("ab", buffering=0) as log_file:
        child = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            while child.poll() is None:
                if stop_file.exists():
                    terminate_group(pgid(child.pid), child.pid, 10.0)
                    break
                time.sleep(0.2)
            return wait_child_or_terminate(child)
        finally:
            stop_file.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
