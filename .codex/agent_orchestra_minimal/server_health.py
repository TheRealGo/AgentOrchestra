from __future__ import annotations

import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Sequence

STARTUP_FAILURE_MARKERS = (
    "address already in use",
    "errno 48",
    "errno 98",
    "eaddrinuse",
    "cannot assign requested address",
    "failed to bind",
    "bind failed",
)


def wait_for_startup(
    process: subprocess.Popen[Any],
    port: int | None,
    timeout: float,
    log_path: Path | None = None,
    settle_time: float = 0.35,
    health_url: str | None = None,
    health_contains: str | None = None,
    health_timeout: float = 1.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + max(timeout, 0.0)
    last_health_error = ""
    while True:
        exit_code = process.poll()
        if exit_code is not None:
            return {"status": "startup-failed", "exit_code": exit_code}
        port_ready = port is None or tcp_listening("127.0.0.1", port)
        if port_ready:
            if health_url:
                health = http_health_check(
                    health_url,
                    contains=health_contains,
                    timeout=health_timeout,
                )
                if health["ok"]:
                    startup = _confirm_stable_startup(process, log_path, settle_time)
                    if startup["status"] == "running":
                        startup["health_url"] = health_url
                    return startup
                last_health_error = str(health.get("error") or "health-check-failed")
            else:
                return _confirm_stable_startup(process, log_path, settle_time)
        if time.monotonic() >= deadline:
            result: dict[str, Any] = {"status": "startup-timeout", "exit_code": None}
            if health_url:
                result["health_url"] = health_url
                result["startup_failure"] = "health-check-timeout"
                result["health_error"] = last_health_error
            return result
        time.sleep(0.1)


def _confirm_stable_startup(
    process: subprocess.Popen[Any],
    log_path: Path | None,
    settle_time: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + max(settle_time, 0.0)
    while True:
        exit_code = process.poll()
        if exit_code is not None:
            return {"status": "startup-failed", "exit_code": exit_code}
        tail = log_tail(log_path) if log_path is not None else ""
        if _contains_startup_failure(tail):
            return {"status": "startup-failed", "exit_code": process.poll(), "startup_failure": "log-marker"}
        if time.monotonic() >= deadline:
            return {"status": "running"}
        time.sleep(0.05)


def _contains_startup_failure(text: str) -> bool:
    folded = text.casefold()
    return any(marker in folded for marker in STARTUP_FAILURE_MARKERS)


def tcp_listening(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


def http_health_check(
    url: str,
    *,
    contains: str | None = None,
    timeout: float = 1.0,
) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=max(timeout, 0.1)) as response:
            body = response.read(65536).decode("utf-8", errors="replace")
            status = int(getattr(response, "status", 200))
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        return {"ok": False, "error": str(exc)}
    if status >= 400:
        return {"ok": False, "status": status, "error": f"http-status-{status}"}
    if contains is not None and contains not in body:
        return {"ok": False, "status": status, "error": "missing-health-contains"}
    return {"ok": True, "status": status}


def log_tail(path: Path, limit: int = 4000) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    return data[-limit:].decode("utf-8", errors="replace")


def command_preview(cmd: Sequence[str]) -> list[str]:
    redacted: list[str] = []
    for part in cmd:
        if any(marker in part.casefold() for marker in ("token", "secret", "password", "apikey", "api_key")):
            redacted.append("<redacted>")
        else:
            redacted.append(part)
    return redacted
