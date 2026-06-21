from __future__ import annotations

from .candidate_ledger import candidate_fields, is_comment_or_blank
from .task_file import SharedTaskFile

UNRESOLVED_DISPOSITIONS = frozenset({"deferred", "blocked", "needs_user"})
ZERO_ISSUE_TOPICS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("cao-intervention", ("cao", "intervention")),
    ("cao-approval", ("cao", "approval")),
    ("approval-userneeded-cleanup", ("approval", "userneeded", "cleanup")),
    ("degraded-delivery", ("degraded", "delivery")),
    ("delivery-defect", ("delivery", "defect")),
    ("auto-drain-failed", ("auto", "drain", "failed")),
    ("queued-consultation", ("queued", "consultation")),
    ("input-not-ready", ("input", "not", "ready")),
    ("unproven-execution-path", ("unproven", "execution", "path")),
    ("service-e2e-approval-replay", ("servicee2e", "approval", "replay")),
    ("service-e2e-defect", ("servicee2e", "defect")),
    ("short-selfe2e-run", ("selfe2e", "short", "run")),
    ("short-selfe2e-minutes", ("selfe2e", "minutes")),
    ("generated-copy-change", ("generatedcopy", "change")),
    ("patch-proposal", ("patch", "proposal")),
)


def self_e2e_zero_issue_blockers(task_file: SharedTaskFile) -> list[str]:
    blockers: list[str] = []
    for section_name in ("Acceptance", "Gates", "Candidates"):
        for item in task_file.sections.get(section_name, []):
            if is_comment_or_blank(item):
                continue
            fields = candidate_fields(item)
            unresolved_marker = fields.get("disposition", "") or fields.get("status", "")
            if unresolved_marker not in UNRESOLVED_DISPOSITIONS:
                continue
            topic = zero_issue_topic_from_item(item, fields)
            if topic:
                ledger_id, _separator, _rest = item.partition(":")
                blockers.append(
                    f"self-e2e-unresolved:{topic}:{ledger_id.strip()}:{unresolved_marker}"
                )
    return blockers


def zero_issue_topic_from_item(item: str, fields: dict[str, str]) -> str:
    for text in (
        fields.get("summary", ""),
        fields.get("verification", ""),
        fields.get("evidence", ""),
        item,
    ):
        if topic := zero_issue_topic(text):
            return topic
    return ""


def zero_issue_topic(text: str) -> str:
    normalized = normalize_evidence(text)
    for topic, terms in ZERO_ISSUE_TOPICS:
        if all(term in normalized for term in terms):
            return topic
    return ""


def normalize_evidence(text: str) -> str:
    return "".join(char for char in text.casefold() if char.isalnum())
