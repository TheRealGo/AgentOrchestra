from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .tmux_targets import required_tmux_pane


def default_mailbox_dir() -> Path:
    run_dir = os.environ.get("AGENT_ORCHESTRA_RUN_DIR")
    if run_dir:
        return Path(run_dir) / "mailbox" / "tmux-peer-consultations"
    return Path.cwd() / ".agent-orchestra-mailbox" / "tmux-peer-consultations"


def enqueue_message(
    *,
    pane: str,
    text: str,
    mailbox_dir: str | Path | None = None,
    sender: str = "",
    topic: str = "",
    reason: str = "input-not-ready",
) -> Path:
    pane = required_tmux_pane(pane)
    if not text.strip():
        raise ValueError("text is required")
    root = Path(mailbox_dir) if mailbox_dir is not None else default_mailbox_dir()
    target_dir = root / _pane_slug(pane)
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = target_dir / f"{timestamp}-{time.time_ns()}.json"
    payload = {
        "version": 1,
        "created_at": timestamp,
        "pane": pane,
        "sender": sender,
        "topic": topic,
        "reason": reason,
        "text": " ".join(text.strip().split()),
    }
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def queued_messages(*, pane: str, mailbox_dir: str | Path | None = None) -> list[Path]:
    pane = required_tmux_pane(pane)
    root = Path(mailbox_dir) if mailbox_dir is not None else default_mailbox_dir()
    target_dir = root / _pane_slug(pane)
    if not target_dir.exists():
        return []
    return sorted(path for path in target_dir.glob("*.json") if path.is_file())


def read_message(path: str | Path) -> dict[str, str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("unsupported mailbox message version")
    pane = required_tmux_pane(data.get("pane"))
    text = str(data.get("text", "")).strip()
    if not text:
        raise ValueError("mailbox message text is required")
    return {
        "pane": pane,
        "text": text,
        "sender": str(data.get("sender", "")),
        "topic": str(data.get("topic", "")),
        "reason": str(data.get("reason", "")),
        "created_at": str(data.get("created_at", "")),
    }


def remove_message(path: str | Path) -> None:
    Path(path).unlink(missing_ok=True)


def _pane_slug(pane: str) -> str:
    return pane.replace("%", "pane-").replace(":", "_")
