from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .autonomy_policy import classify_service_e2e_approval_replay
from .completion_profiles import service_defect_intake_items
from .manifest_lock import manifest_lock
from .task_file import SECTION_NAMES, SharedTaskFile
from .user_needed import classify_intervention


@dataclass(frozen=True)
class ServiceE2EDefect:
    defect_id: str
    symptom: str
    workaround: str
    desired_behavior: str
    expected_regression: str


def render_self_improvement_intake(defect: ServiceE2EDefect) -> dict[str, str]:
    defect_id = _ledger_id(defect.defect_id)
    _require_field("symptom", defect.symptom)
    _require_field("workaround", defect.workaround)
    _require_field("desired_behavior", defect.desired_behavior)
    _require_field("expected_regression", defect.expected_regression)
    evidence = f"service-e2e-intake:{defect_id}"
    summary = _compact(defect.symptom)
    return {
        "Backlog": (
            f"{defect_id}: owner_dri=main; scope=AgentOrchestra service-E2E defect intake; "
            f"summary={summary}; evidence={evidence}"
        ),
        "Acceptance": (
            f"{defect_id}-acceptance: status=open; source=service-e2e-defect; owner=main; "
            f"verification={_compact(defect.expected_regression)}; evidence=pending"
        ),
        "Gates": (
            f"{defect_id}-regression: status=open; kind=e2e; "
            f"evidence=expected:{_compact(defect.expected_regression)}"
        ),
        "Candidates": (
            f"{defect_id}-candidate: disposition=open; summary={summary}; evidence={evidence}"
        ),
    }


def render_self_improvement_intake_from_brief(defect_brief: str) -> dict[str, list[str]]:
    if not defect_brief.strip():
        raise ValueError("defect_brief is required")
    rendered: dict[str, list[str]] = {"Backlog": [], "Acceptance": [], "Gates": [], "Candidates": []}
    for defect_id in service_defect_intake_items(defect_brief):
        summary = defect_id.replace("-", " ")
        item = render_self_improvement_intake(
            ServiceE2EDefect(
                defect_id=defect_id,
                symptom=f"ServiceE2E observed AgentOrchestra defect: {summary}",
                workaround="CAO intervention or workaround was required during service E2E",
                desired_behavior="AgentOrchestra records the issue in SelfE2E backlog/acceptance and fixes or keeps status progress",
                expected_regression=f"focused regression covers {summary}",
            )
        )
        for section, line in item.items():
            rendered[section].append(line)
    if _mentions_service_e2e_approval_replay(defect_brief):
        replay = render_service_e2e_approval_replay_intake()
        for section, lines in replay.items():
            rendered[section].extend(lines)
    return rendered


def append_self_improvement_intake_to_task_file(
    *,
    task_file_path: str | Path,
    defect_brief: str,
) -> dict[str, list[str]]:
    rendered = render_self_improvement_intake_from_brief(defect_brief)
    path = Path(task_file_path)
    with manifest_lock(path):
        task_file = SharedTaskFile.read(path)
        sections = {name: list(task_file.sections.get(name, [])) for name in SECTION_NAMES}
        for section in ("Backlog", "Acceptance", "Gates", "Candidates"):
            existing_ids = {
                _ledger_line_id(line): index
                for index, line in enumerate(sections.get(section, []))
                if _ledger_line_id(line)
            }
            for line in rendered[section]:
                ledger_id = _ledger_line_id(line)
                if not ledger_id:
                    continue
                if ledger_id in existing_ids:
                    sections[section][existing_ids[ledger_id]] = line
                else:
                    sections[section].append(line)
                    existing_ids[ledger_id] = len(sections[section]) - 1
        _write_task_file(path, status="progress", sections=sections)
    return rendered


def render_service_e2e_approval_replay_intake() -> dict[str, list[str]]:
    rendered: dict[str, list[str]] = {"Backlog": [], "Acceptance": [], "Gates": [], "Candidates": []}
    for observation, classification in classify_service_e2e_approval_replay():
        if classification.category != observation.expected_category:
            raise ValueError(
                f"{observation.defect_id} classified as {classification.category}, "
                f"expected {observation.expected_category}"
            )
        intervention = classify_intervention(
            reason="codex approval prompt",
            in_edit_root=True,
            low_risk=False,
            command=observation.command,
            current_run_scope=observation.current_run_scope,
            process_identity_known=observation.process_identity_known,
            port_owned=observation.port_owned,
        )
        if intervention.disposition != "autonomy_blocker" or intervention.ledger_status != "open":
            raise ValueError(
                f"{observation.defect_id} approval prompt routed to "
                f"{intervention.disposition}/{intervention.ledger_status}, expected autonomy_blocker/open"
            )
        defect_id = f"service-e2e-approval-replay-{observation.defect_id}"
        command = _compact(observation.command)
        evidence = f"service-e2e-approval-replay:{observation.defect_id}"
        summary = (
            f"ServiceE2E approval/UserNeeded replay command {command} "
            f"classifies as {classification.category} and approval prompt disposition {intervention.disposition}"
        )
        item = render_self_improvement_intake(
            ServiceE2EDefect(
                defect_id=defect_id,
                symptom=summary,
                workaround="CAO approval or manual command execution was observed during ServiceE2E",
                desired_behavior=(
                    "AgentOrchestra routes this command through the autonomy policy "
                    "and keeps any approval prompt as SelfE2E defect evidence"
                ),
                expected_regression=(
                    f"replay classifies command as {classification.category} "
                    f"with ledger_status {classification.ledger_status} and "
                    f"approval prompt routes through UserNeeded disposition {intervention.disposition} "
                    f"with ledger_status {intervention.ledger_status}"
                ),
            )
        )
        for section, line in item.items():
            rendered[section].append(line.replace(f"evidence=service-e2e-intake:{defect_id}", f"evidence={evidence}"))
    return rendered


def _mentions_service_e2e_approval_replay(defect_brief: str) -> bool:
    text = defect_brief.casefold()
    compact = "".join(char for char in text if char.isalnum())
    return "servicee2e" in compact and (
        "approval" in text or "userneeded" in text or "user needed" in text or "cleanup" in text
    )


def _ledger_id(value: str) -> str:
    cleaned = value.strip().casefold().replace(" ", "-").replace("_", "-")
    if not cleaned or ":" in cleaned or ";" in cleaned:
        raise ValueError("defect_id must be a non-empty ledger-safe value")
    return cleaned


def _ledger_line_id(line: str) -> str:
    ledger_id, separator, _rest = line.partition(":")
    return _ledger_id(ledger_id) if separator else ""


def _write_task_file(path: Path, *, status: str, sections: dict[str, list[str]]) -> None:
    lines: list[str] = []
    for section in SECTION_NAMES:
        lines.append(f"[{section}]")
        if section == "status":
            lines.append(status)
        else:
            lines.extend(sections.get(section, []))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _require_field(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} is required")


def _compact(value: str) -> str:
    return " ".join(value.strip().split()).replace(";", ",")
