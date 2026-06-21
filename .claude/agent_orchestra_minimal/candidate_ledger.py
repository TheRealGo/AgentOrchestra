from __future__ import annotations


COMPLETED_CANDIDATE_DISPOSITIONS = frozenset(
    {"integrated", "rejected", "deferred", "blocked", "out-of-scope", "needs_user"}
)
OPEN_CANDIDATE_DISPOSITIONS = frozenset({"", "open", "backlog"})
PLACEHOLDER_CANDIDATE_EVIDENCE = frozenset({"pending", "tbd", "todo", "unknown"})


def unresolved_candidate_items(items: list[str]) -> list[str]:
    return [
        item
        for item in items
        if not is_comment_or_blank(item)
        and candidate_disposition(item) not in COMPLETED_CANDIDATE_DISPOSITIONS
    ]


def validate_unique_candidate_ids(items: list[str]) -> None:
    seen: set[str] = set()
    for item in items:
        if is_comment_or_blank(item):
            continue
        candidate_id, separator, _rest = item.partition(":")
        if not separator:
            continue
        normalized = candidate_id_key(candidate_id)
        if not normalized:
            continue
        if normalized in seen:
            raise ValueError(f"duplicate candidate id {normalized!r}")
        seen.add(normalized)


def candidate_disposition(item: str) -> str:
    if candidate_has_duplicate_fields(item):
        return "open"
    fields = candidate_fields(item)
    disposition = fields.get("disposition", "")
    if disposition in COMPLETED_CANDIDATE_DISPOSITIONS:
        if candidate_has_required_evidence(item, fields):
            return disposition
        return "open"
    if disposition in OPEN_CANDIDATE_DISPOSITIONS:
        return disposition
    return "open"


def candidate_fields(item: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for index, part in enumerate(item.split(";")):
        normalized = part.strip()
        if index == 0 and ":" in normalized:
            normalized = normalized.split(":", 1)[1].strip()
        key, separator, value = normalized.partition("=")
        if separator:
            fields[candidate_field_key(key)] = value.strip()
    return fields


def candidate_has_duplicate_fields(item: str) -> bool:
    seen: set[str] = set()
    for index, part in enumerate(item.split(";")):
        normalized = part.strip()
        if index == 0 and ":" in normalized:
            normalized = normalized.split(":", 1)[1].strip()
        key, separator, _value = normalized.partition("=")
        if not separator:
            continue
        normalized_key = candidate_field_key(key)
        if normalized_key in seen:
            return True
        seen.add(normalized_key)
    return False


def candidate_field_key(key: str) -> str:
    return key.strip().lower()


def candidate_has_required_evidence(item: str, fields: dict[str, str]) -> bool:
    candidate_id, separator, _rest = item.partition(":")
    evidence = fields.get("evidence", "").strip()
    return bool(
        separator
        and candidate_id.strip()
        and fields.get("summary", "").strip()
        and evidence
        and evidence.casefold() not in PLACEHOLDER_CANDIDATE_EVIDENCE
    )


def candidate_id_key(candidate_id: str) -> str:
    return candidate_id.strip().casefold()


def is_comment_or_blank(item: str) -> bool:
    stripped = item.strip()
    return not stripped or stripped.startswith("#") or stripped.startswith(";")
