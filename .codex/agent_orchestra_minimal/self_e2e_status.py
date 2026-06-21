from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .autonomy_policy import SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS
from .candidate_ledger import candidate_fields, is_comment_or_blank
from .self_e2e_active_main import active_main_binding_blockers
from .self_e2e_zero_issue import self_e2e_zero_issue_blockers
from .task_file import SharedTaskFile


SELF_E2E_REQUIRED_EVIDENCE: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("service-approval-replay", ("servicee2eintake", "workerpath", "replay", "approval")),
    ("execution-path-proof", ("executionpath",)),
    ("multi-viewpoint-search", ("multiviewpoint", "search")),
    ("professional-agent-review", ("professionalagent",)),
    ("standard-verification", ("standardverification",)),
    ("final-candidate-sweep", ("candidatesweep",)),
    ("cao-intervention-disposition", ("cao", "intervention")),
    ("live-main-self-exit-json", ("mainselfexit", "json", "copiedruntime", "closedtrue")),
    ("same-session-auxiliary-shell-cleanup", ("auxiliaryshellpanes", "samesession")),
    ("dedicated-session-gone", ("dedicatedsessiongone",)),
    ("active-main-session-binding", ("activemainsession", "pane", "session")),
    ("no-cao-cleanup", ("nocaocleanup",)),
)
@dataclass(frozen=True)
class SelfE2EStatusEvidence:
    status_path: str
    task_file_path: str
    observed_content: str
    task_file_finalized: bool

    @property
    def value(self) -> str:
        return self.observed_content

    @property
    def readback(self) -> str:
        return self.observed_content


@dataclass(frozen=True)
class SelfE2EStatusResult:
    status: str
    observed: str
    task_finalized: bool
    blockers: tuple[str, ...]


class SelfE2EStatusError(ValueError):
    def __init__(self, blockers: list[str]) -> None:
        super().__init__("SelfE2E status cannot be done while task ledger is unresolved")
        self.blockers = blockers


class TaskFileNotFinalizedError(SelfE2EStatusError):
    pass


def write_progress_or_done_after_task_finalization(
    *,
    task_file_path: str | Path,
    status_path: str | Path,
    active_main_pane: str | None = None,
    active_main_session_name: str | None = None,
    self_exit_result_path: str | Path | None = None,
) -> SelfE2EStatusEvidence:
    task_path = Path(task_file_path)
    status = Path(status_path)
    task_file = SharedTaskFile.read(task_path)
    blockers = _self_e2e_finalization_blockers(
        task_file,
        status_path=status,
        active_main_pane=active_main_pane,
        active_main_session_name=active_main_session_name,
        self_exit_result_path=self_exit_result_path,
    )
    if blockers:
        status.parent.mkdir(parents=True, exist_ok=True)
        status.write_text("progress", encoding="utf-8")
        observed = status.read_text(encoding="utf-8")
        raise TaskFileNotFinalizedError(blockers + [f"status-observed:{observed}"])

    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text("done", encoding="utf-8")
    observed = status.read_text(encoding="utf-8")
    if observed != "done":
        raise SelfE2EStatusError([f"status-readback-mismatch:{observed!r}"])
    return SelfE2EStatusEvidence(
        status_path=str(status),
        task_file_path=str(task_path),
        observed_content=observed,
        task_file_finalized=True,
    )


def write_done_after_task_finalization(
    *,
    task_file: str | Path,
    status_file: str | Path,
    active_main_pane: str | None = None,
    active_main_session_name: str | None = None,
    self_exit_result_path: str | Path | None = None,
) -> SelfE2EStatusEvidence:
    return write_progress_or_done_after_task_finalization(
        task_file_path=task_file,
        status_path=status_file,
        active_main_pane=active_main_pane,
        active_main_session_name=active_main_session_name,
        self_exit_result_path=self_exit_result_path,
    )


def finalize_status_after_task_readback(
    *,
    status_path: str | Path,
    task_file_path: str | Path,
    active_main_pane: str | None = None,
    active_main_session_name: str | None = None,
    self_exit_result_path: str | Path | None = None,
) -> SelfE2EStatusResult:
    status_file = Path(status_path)
    task_file = SharedTaskFile.read(task_file_path)
    status_file.parent.mkdir(parents=True, exist_ok=True)

    blockers = _self_e2e_finalization_blockers(
        task_file,
        status_path=status_file,
        active_main_pane=active_main_pane,
        active_main_session_name=active_main_session_name,
        self_exit_result_path=self_exit_result_path,
    )
    if blockers:
        status_file.write_text("progress", encoding="utf-8")
        observed = status_file.read_text(encoding="utf-8")
        return SelfE2EStatusResult(
            status="progress",
            observed=observed,
            task_finalized=False,
            blockers=tuple(blockers),
        )

    evidence = write_progress_or_done_after_task_finalization(
        task_file_path=task_file_path,
        status_path=status_file,
        active_main_pane=active_main_pane,
        active_main_session_name=active_main_session_name,
        self_exit_result_path=self_exit_result_path,
    )
    return SelfE2EStatusResult(
        status=evidence.observed_content,
        observed=evidence.observed_content,
        task_finalized=True,
        blockers=(),
    )


def _self_e2e_finalization_blockers(
    task_file: SharedTaskFile,
    *,
    status_path: str | Path | None = None,
    active_main_pane: str | None = None,
    active_main_session_name: str | None = None,
    self_exit_result_path: str | Path | None = None,
) -> list[str]:
    blockers = list(task_file.finalization_blockers)
    if blockers:
        return blockers
    evidence_text = _normalize_evidence(" ".join(_resolved_ledger_evidence_items(task_file)))
    for evidence_id, required_terms in SELF_E2E_REQUIRED_EVIDENCE:
        if not all(term in evidence_text for term in required_terms):
            blockers.append(f"self-e2e-missing:{evidence_id}")
    blockers.extend(_service_e2e_replay_evidence_blockers(evidence_text))
    blockers.extend(self_e2e_zero_issue_blockers(task_file))
    if not blockers and status_path is not None:
        blockers.extend(
            _self_exit_result_blockers(
                Path(status_path),
                active_main_pane=active_main_pane,
                active_main_session_name=active_main_session_name,
                self_exit_result_path=self_exit_result_path,
            )
        )
    return blockers


def _self_exit_result_blockers(
    status_path: Path,
    *,
    active_main_pane: str | None = None,
    active_main_session_name: str | None = None,
    self_exit_result_path: str | Path | None = None,
) -> list[str]:
    result_path = (
        Path(self_exit_result_path)
        if self_exit_result_path is not None
        else _latest_self_exit_result_path(status_path)
    )
    if result_path is None:
        return ["self-e2e-missing:live-main-self-exit-json"]
    if not result_path.is_file():
        return ["self-e2e-missing:live-main-self-exit-json"]
    payload, load_blockers = _load_self_exit_payload(result_path)
    if load_blockers:
        return load_blockers
    return _validate_self_exit_payload(
        status_path.parent,
        payload,
        active_main_pane=active_main_pane,
        active_main_session_name=active_main_session_name,
    )


def _load_self_exit_payload(result_path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"self-e2e-invalid:live-main-self-exit-json:{exc.__class__.__name__}"]
    if not isinstance(payload, dict):
        return {}, ["self-e2e-invalid:live-main-self-exit-json:not-object"]
    return payload, []


def _validate_self_exit_payload(
    status_dir: Path,
    payload: dict[str, Any],
    *,
    active_main_pane: str | None = None,
    active_main_session_name: str | None = None,
) -> list[str]:
    blockers: list[str] = []
    if payload.get("closed") is not True:
        blockers.append("self-e2e-invalid:live-main-self-exit-json:closed-not-true")
    expected_pane = active_main_pane.strip() if active_main_pane is not None else ""
    if expected_pane and _string_field(payload, "pane") != expected_pane:
        blockers.append("self-e2e-invalid:active-main-pane-binding")
    expected_session_name = active_main_session_name.strip() if active_main_session_name is not None else ""
    session_name = _string_field(payload, "session_name")
    if expected_session_name and session_name != expected_session_name:
        blockers.append("self-e2e-invalid:active-main-session-binding")
    if not session_name.startswith("AgentOrchestra-self-e2e-"):
        blockers.append("self-e2e-invalid:same-session-auxiliary-shell-cleanup:session-prefix")
    auxiliary_shell_panes = payload.get("auxiliary_shell_panes")
    if not isinstance(auxiliary_shell_panes, list) or not all(
        isinstance(pane, str) and pane.startswith("%") for pane in auxiliary_shell_panes
    ):
        blockers.append("self-e2e-invalid:same-session-auxiliary-shell-cleanup:auxiliary-shell-panes")
    if payload.get("session_gone") is not True:
        blockers.append("self-e2e-invalid:dedicated-session-gone")
    reason = _string_field(payload, "reason").casefold()
    if "cao" in reason or "cao" in session_name.casefold():
        blockers.append("self-e2e-invalid:no-cao-cleanup")
    blockers.extend(active_main_binding_blockers(status_dir, payload))
    return blockers


def _latest_self_exit_result_path(status_path: Path) -> Path | None:
    status_dir = status_path.parent
    candidates = sorted(
        (path for path in status_dir.glob("main-self-exit*.json") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _string_field(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    return value if isinstance(value, str) else ""


def _resolved_ledger_evidence_items(task_file: SharedTaskFile) -> list[str]:
    items: list[str] = []
    for section_name in ("Acceptance", "Gates", "Candidates", "Done"):
        for item in task_file.sections.get(section_name, []):
            if is_comment_or_blank(item):
                continue
            fields = candidate_fields(item)
            items.append(item)
            evidence = fields.get("evidence", "").strip()
            if evidence:
                items.append(evidence)
    return items


def _normalize_evidence(text: str) -> str:
    return "".join(char for char in text.casefold() if char.isalnum())


def _service_e2e_replay_evidence_blockers(evidence_text: str) -> list[str]:
    if "servicee2eintake" not in evidence_text or "replay" not in evidence_text:
        return []
    return [
        f"self-e2e-missing:service-approval-replay:{observation.defect_id}"
        for observation in SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS
        if _normalize_evidence(f"service-e2e-approval-replay-{observation.defect_id}") not in evidence_text
    ]
