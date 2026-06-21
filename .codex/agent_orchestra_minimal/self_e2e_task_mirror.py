from __future__ import annotations

from pathlib import Path

from .self_e2e_status import SelfE2EStatusResult
from .task_file import SECTION_NAMES, SharedTaskFile


def mirror_self_e2e_blockers_to_task_file(
    *,
    task_file_path: str | Path,
    status: SelfE2EStatusResult,
) -> None:
    if status.status == "done" or not status.blockers:
        return
    path = Path(task_file_path)
    task_file = SharedTaskFile.read(path)
    if task_file.status != "done":
        return

    sections = {name: list(task_file.sections.get(name, [])) for name in SECTION_NAMES}
    existing_candidate_ids = {
        item.partition(":")[0].strip().casefold()
        for item in sections.get("Candidates", [])
        if item.partition(":")[1]
    }
    for blocker in status.blockers:
        candidate_id = f"selfe2e-finalizer-{_candidate_slug(blocker)}"
        if candidate_id.casefold() in existing_candidate_ids:
            continue
        sections["Candidates"].append(
            f"{candidate_id}: disposition=open; "
            "summary=SelfE2E finalizer blocker prevents copied status done; "
            f"evidence={_candidate_evidence(blocker)}"
        )
        existing_candidate_ids.add(candidate_id.casefold())

    path.write_text(_render_task_file("progress", sections), encoding="utf-8")


def _candidate_slug(text: str) -> str:
    chars: list[str] = []
    previous_dash = False
    for char in text.casefold():
        if char.isalnum():
            chars.append(char)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True
    return ("".join(chars).strip("-") or "unknown")[:96]


def _candidate_evidence(text: str) -> str:
    return text.replace(";", ",").strip() or "unknown"


def _render_task_file(status: str, sections: dict[str, list[str]]) -> str:
    rendered: list[str] = ["[status]", status, ""]
    for section in SECTION_NAMES:
        if section == "status":
            continue
        rendered.append(f"[{section}]")
        rendered.extend(sections.get(section, []))
        rendered.append("")
    return "\n".join(rendered).rstrip() + "\n"
