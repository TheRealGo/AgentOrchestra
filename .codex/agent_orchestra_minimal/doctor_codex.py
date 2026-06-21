from __future__ import annotations

import json
import re
import subprocess
from typing import Any


SECRET_ASSIGNMENT = re.compile(r"\b((?:[A-Za-z0-9_]*_)?token)=([^\s,)]+)", re.IGNORECASE)


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
            summary = _redact_diagnostic_text(str(check.get("summary", "")).strip())
            line = f"Codex doctor {check_status}: {category}/{check_id}"
            if summary:
                line = f"{line}: {summary}"
            remediation = _redact_diagnostic_text(str(check.get("remediation", "") or "").strip())
            if remediation:
                line = f"{line} ({remediation})"
            lines.append(line)

    if len(lines) == 1 and status == "ok":
        lines[0] = f"Codex doctor ok version={version}"
    return CodexDoctorReport(failed=failed, lines=lines)


def _redact_diagnostic_text(text: str) -> str:
    return SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=<redacted>", text)
