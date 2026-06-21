from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ACTIVE_MAIN_SESSION_FILENAMES = (
    "active-main-session.json",
    "main-session.json",
)


def active_main_binding_blockers(status_dir: Path, payload: dict[str, Any]) -> list[str]:
    identity_path = _active_main_identity_path(status_dir)
    if identity_path is None:
        return ["self-e2e-missing:active-main-session-binding"]
    try:
        identity = json.loads(identity_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"self-e2e-invalid:active-main-session-binding:{exc.__class__.__name__}"]
    if not isinstance(identity, dict):
        return ["self-e2e-invalid:active-main-session-binding:not-object"]

    blockers: list[str] = []
    expected_pane = _first_string_field(identity, "pane", "main_pane", "active_main_pane")
    expected_session = _first_string_field(
        identity,
        "session_name",
        "main_session_name",
        "active_main_session",
    )
    if not expected_pane.startswith("%"):
        blockers.append("self-e2e-invalid:active-main-session-binding:pane")
    if not expected_session.startswith("AgentOrchestra-self-e2e-"):
        blockers.append("self-e2e-invalid:active-main-session-binding:session-name")
    if blockers:
        return blockers

    if _string_field(payload, "pane") != expected_pane:
        blockers.append("self-e2e-invalid:active-main-session-binding:pane-mismatch")
    if _string_field(payload, "session_name") != expected_session:
        blockers.append("self-e2e-invalid:active-main-session-binding:session-mismatch")
    return blockers


def _active_main_identity_path(status_dir: Path) -> Path | None:
    for filename in ACTIVE_MAIN_SESSION_FILENAMES:
        path = status_dir / filename
        if path.is_file():
            return path
    return None


def _string_field(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    return value if isinstance(value, str) else ""


def _first_string_field(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""
