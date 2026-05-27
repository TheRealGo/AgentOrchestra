from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .candidate_ledger import (
    is_comment_or_blank,
    unresolved_candidate_items,
    validate_unique_candidate_ids,
)


SECTION_NAMES = ("status", "Backlog", "InProgress", "InReview", "Candidates", "Done")
OPEN_WORK_SECTIONS = ("Backlog", "InProgress", "InReview")
ALLOWED_STATUS = frozenset({"progress", "done"})
DEFAULT_TASK_FILE = """[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]

[Done]
"""


@dataclass(frozen=True)
class SharedTaskFile:
    status: str
    sections: dict[str, list[str]]

    @classmethod
    def parse(cls, text: str) -> "SharedTaskFile":
        current: str | None = None
        sections: dict[str, list[str]] = {name: [] for name in SECTION_NAMES}
        seen_sections: set[str] = set()

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1].strip()
                if current not in SECTION_NAMES:
                    raise ValueError(f"unknown shared task file section {current!r}")
                if current in seen_sections:
                    raise ValueError(f"duplicate shared task file section {current!r}")
                seen_sections.add(current)
                continue
            if current is None:
                raise ValueError("shared task file content must appear under a required section")
            sections[current].append(line if current == "status" else _normalize_item(line))

        missing = [name for name in SECTION_NAMES if name not in seen_sections]
        if missing:
            raise ValueError(f"shared task file missing required sections: {', '.join(missing)}")

        status_values = sections.get("status", [])
        if len(status_values) != 1:
            raise ValueError("shared task file [status] must contain exactly one value")
        status = status_values[0].strip()
        if status not in ALLOWED_STATUS:
            raise ValueError(f"invalid shared task status {status!r}")
        validate_unique_candidate_ids(sections["Candidates"])
        return cls(status=status, sections=sections)

    @classmethod
    def read(cls, path: str | Path) -> "SharedTaskFile":
        return cls.parse(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def initialize(cls, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(DEFAULT_TASK_FILE, encoding="utf-8")
        target.chmod(0o600)
        return target

    @property
    def open_work_items(self) -> list[str]:
        items: list[str] = []
        for section in OPEN_WORK_SECTIONS:
            items.extend(
                item
                for item in self.sections.get(section, [])
                if not is_comment_or_blank(item)
            )
        return items

    @property
    def has_open_work(self) -> bool:
        return bool(self.open_work_items)

    @property
    def candidate_items(self) -> list[str]:
        return [
            item
            for item in self.sections.get("Candidates", [])
            if not is_comment_or_blank(item)
        ]

    @property
    def unresolved_candidate_items(self) -> list[str]:
        return unresolved_candidate_items(self.candidate_items)

    @property
    def has_unresolved_candidates(self) -> bool:
        return bool(self.unresolved_candidate_items)

    @property
    def finalization_blockers(self) -> list[str]:
        blockers: list[str] = []
        if self.status != "done":
            blockers.append(f"status={self.status}")
        blockers.extend(f"open:{item}" for item in self.open_work_items)
        blockers.extend(
            f"candidate:{item}" for item in self.unresolved_candidate_items
        )
        return blockers

    @property
    def is_finalized(self) -> bool:
        return not self.finalization_blockers


def _normalize_item(line: str) -> str:
    for prefix in ("- ", "* "):
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return line
