from __future__ import annotations

import json
from pathlib import Path

from .tmux_delivery import DEFAULT_SUBMIT_KEY, DeliveryResult, normalize_submit_key


def _write_result_json(
    path: Path,
    *,
    pane: str,
    result: DeliveryResult,
    submit_key: str = DEFAULT_SUBMIT_KEY,
    queued_path: Path | None = None,
    auto_drain_result: dict[str, object] | None = None,
) -> None:
    expected_fallback = _expected_nonstandard_submit_key_fallback(result, submit_key)
    degraded = result.accepted and result.attempts > 1 and not expected_fallback
    failure_phase = _failure_phase(result)
    queued = queued_path is not None
    _write_json(
        path,
        {
            "pane": pane,
            "accepted": result.accepted,
            "attempts": result.attempts,
            "degraded": degraded,
            "expected_submit_key_fallback": expected_fallback,
            "failure_phase": failure_phase,
            "queued": queued,
            "queue_path": str(queued_path) if queued_path is not None else "",
            "auto_drain": auto_drain_result or {},
            "ledger_candidate": _ledger_candidate(degraded=degraded, accepted=result.accepted, queued=queued),
            "zero_issue_blocker": degraded or (not result.accepted and not queued),
            "required_disposition": _required_disposition(degraded=degraded, queued=queued, accepted=result.accepted, failure_phase=failure_phase),
            "capture_tail": result.capture_tail,
        },
    )


def _write_drain_result_json(path: Path, *, pane: str, result: dict[str, object]) -> None:
    failed = int(result["failed"])
    _write_json(
        path,
        {
            "pane": pane,
            "mailbox_drain": True,
            **result,
            "accepted": failed == 0,
            "ledger_candidate": "" if failed == 0 else "delivery-defect",
            "zero_issue_blocker": failed != 0,
            "required_disposition": "" if failed == 0 else "keep queued consultation unresolved and retry drain after the target pane is input-ready",
        },
    )


def _write_auto_drain_failure_result_json(path: Path, *, pane: str, result: dict[str, object]) -> None:
    _write_json(
        path,
        {
            "pane": pane,
            "accepted": False,
            "attempts": 0,
            "degraded": False,
            "expected_submit_key_fallback": False,
            "failure_phase": "auto-drain-failed",
            "queued": False,
            "queue_path": "",
            "auto_drain": result,
            "new_message_sent": False,
            "ledger_candidate": "delivery-defect",
            "zero_issue_blocker": True,
            "required_disposition": "auto-drain failed before new send; keep queued consultation unresolved and retry drain after the target pane is input-ready",
            "capture_tail": _first_failed_capture_tail(result),
        },
    )


def _failure_phase(result: DeliveryResult) -> str:
    if result.accepted:
        return ""
    return "input-not-ready" if result.attempts == 0 else "submitted-unaccepted"


def _expected_nonstandard_submit_key_fallback(result: DeliveryResult, submit_key: str) -> bool:
    key = normalize_submit_key(submit_key)
    return bool(result.accepted and result.attempts == 2 and key not in {"C-m", "C-j"})


def _ledger_candidate(*, degraded: bool, accepted: bool, queued: bool) -> str:
    if degraded or (not accepted and not queued):
        return "delivery-defect"
    return "queued-consultation" if queued else ""


def _required_disposition(*, degraded: bool, queued: bool, accepted: bool, failure_phase: str) -> str:
    if degraded:
        return "record unresolved Gates/Candidates evidence before clean completion"
    if queued:
        return "drain queued consultation after the target pane becomes input-ready and record accepted drain evidence"
    if failure_phase == "input-not-ready":
        return "block completion until the target pane is input-ready, then retry or relaunch with evidence"
    return "block completion until delivery succeeds or is dispositioned" if not accepted else ""


def _first_failed_capture_tail(result: dict[str, object]) -> str:
    failed_messages = result.get("failed_messages")
    if not isinstance(failed_messages, list) or not failed_messages:
        return ""
    first = failed_messages[0]
    if not isinstance(first, dict):
        return ""
    capture_tail = first.get("capture_tail")
    return capture_tail if isinstance(capture_tail, str) else ""


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
