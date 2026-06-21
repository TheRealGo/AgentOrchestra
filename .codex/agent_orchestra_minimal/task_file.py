from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .candidate_ledger import (
    candidate_fields,
    candidate_has_duplicate_fields,
    candidate_id_key,
    is_comment_or_blank,
    unresolved_candidate_items,
    validate_unique_candidate_ids,
)
from .manifest_lock import manifest_lock


SECTION_NAMES = ("status", "Backlog", "InProgress", "InReview", "Acceptance", "Gates", "Candidates", "Done")
REQUIRED_SECTION_NAMES = ("status", "Backlog", "InProgress", "InReview", "Candidates", "Done")
OPEN_WORK_SECTIONS = ("Backlog", "InProgress", "InReview")
ALLOWED_STATUS = frozenset({"progress", "done"})
RESOLVED_ACCEPTANCE_STATUS = frozenset({"satisfied", "out-of-scope", "deferred"})
RESOLVED_GATE_STATUS = frozenset({"passed", "not-applicable"})
GATE_KINDS = frozenset({"visual", "mcp", "env", "test", "e2e"})
PLACEHOLDER_EVIDENCE_VALUES = frozenset({"pending", "tbd", "todo", "unknown"})
VISUAL_GATE_EVIDENCE_KEYS = (
    "url",
    "viewport",
    "viewport_actual",
    "screenshot",
    "console",
    "network",
    "agent",
    "server_manifest",
    "assertions",
    "artifact_dir",
    "fit",
    "cleanup",
)
DEFAULT_TASK_FILE = """[status]
done

[Backlog]

[InProgress]

[InReview]

[Acceptance]

[Gates]

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

        missing = [name for name in REQUIRED_SECTION_NAMES if name not in seen_sections]
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
    def initialize(cls, path: str | Path, *, status: str = "done") -> Path:
        if status not in ALLOWED_STATUS:
            raise ValueError(f"invalid initial shared task status {status!r}")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with manifest_lock(target):
            if not target.exists():
                target.write_text(
                    DEFAULT_TASK_FILE.replace("[status]\ndone", f"[status]\n{status}", 1),
                    encoding="utf-8",
                )
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
    def acceptance_items(self) -> list[str]:
        return [
            item
            for item in self.sections.get("Acceptance", [])
            if not is_comment_or_blank(item)
        ]

    @property
    def unresolved_acceptance_items(self) -> list[str]:
        return _unresolved_ledger_items(
            self.acceptance_items,
            resolved_statuses=RESOLVED_ACCEPTANCE_STATUS,
            required_fields=("status", "source", "owner", "verification", "evidence"),
        )

    @property
    def has_unresolved_acceptance(self) -> bool:
        return bool(self.unresolved_acceptance_items)

    @property
    def gate_items(self) -> list[str]:
        return [
            item
            for item in self.sections.get("Gates", [])
            if not is_comment_or_blank(item)
        ]

    @property
    def unresolved_gate_items(self) -> list[str]:
        return _unresolved_ledger_items(
            self.gate_items,
            resolved_statuses=RESOLVED_GATE_STATUS,
            required_fields=("status", "kind", "evidence"),
            allowed_kinds=GATE_KINDS,
        )

    @property
    def has_unresolved_gates(self) -> bool:
        return bool(self.unresolved_gate_items)

    @property
    def finalization_blockers(self) -> list[str]:
        blockers: list[str] = []
        if self.status != "done":
            blockers.append(f"status={self.status}")
        blockers.extend(f"open:{item}" for item in self.open_work_items)
        blockers.extend(
            f"acceptance-duplicate:{item}"
            for item in _duplicate_ledger_id_items(self.acceptance_items)
        )
        blockers.extend(
            f"acceptance:{item}" for item in self.unresolved_acceptance_items
        )
        blockers.extend(
            f"gate-duplicate:{item}"
            for item in _duplicate_ledger_id_items(self.gate_items)
        )
        blockers.extend(f"gate:{item}" for item in self.unresolved_gate_items)
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


def _unresolved_ledger_items(
    items: list[str],
    *,
    resolved_statuses: frozenset[str],
    required_fields: tuple[str, ...],
    allowed_kinds: frozenset[str] | None = None,
) -> list[str]:
    unresolved: list[str] = []
    for item in items:
        fields = candidate_fields(item)
        if (
            not _ledger_has_id(item)
            or candidate_has_duplicate_fields(item)
            or any(not fields.get(field, "").strip() for field in required_fields)
            or _has_placeholder_evidence(fields)
            or fields.get("status", "") not in resolved_statuses
            or (allowed_kinds is not None and fields.get("kind", "") not in allowed_kinds)
            or _visual_gate_evidence_is_incomplete(fields)
        ):
            unresolved.append(item)
    return unresolved


def _ledger_has_id(item: str) -> bool:
    ledger_id, separator, _rest = item.partition(":")
    return bool(separator and ledger_id.strip())


def _duplicate_ledger_id_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for item in items:
        if is_comment_or_blank(item):
            continue
        ledger_id, separator, _rest = item.partition(":")
        if not separator:
            continue
        normalized = candidate_id_key(ledger_id)
        if not normalized:
            continue
        if normalized in seen:
            duplicates.append(item)
            continue
        seen.add(normalized)
    return duplicates


def _has_placeholder_evidence(fields: dict[str, str]) -> bool:
    evidence = fields.get("evidence", "").strip().casefold()
    return evidence in PLACEHOLDER_EVIDENCE_VALUES


def _visual_gate_evidence_is_incomplete(fields: dict[str, str]) -> bool:
    if fields.get("status") != "passed" or fields.get("kind") != "visual":
        return False
    evidence = fields.get("evidence", "")
    folded_evidence = evidence.casefold()
    if any(not (fields.get(key, "").strip() or f"{key}=" in folded_evidence) for key in VISUAL_GATE_EVIDENCE_KEYS):
        return True
    requested = fields.get("viewport", "").strip() or _evidence_value(evidence, "viewport")
    actual = fields.get("viewport_actual", "").strip() or _evidence_value(evidence, "viewport_actual")
    return not requested or requested != actual


def _evidence_value(evidence: str, key: str) -> str:
    prefix = f"{key}="
    for token in evidence.split():
        if token.startswith(prefix):
            return token[len(prefix) :].strip()
    return ""
