from __future__ import annotations

from dataclasses import dataclass


ACTIVE_STATES = frozenset({"working", "ready", "ready_for_review"})
STALE_STATES = frozenset({"usage_limited", "working_stale", "interrupted_or_paused", "unsupported_model"})


@dataclass(frozen=True)
class PaneRecord:
    agent_id: str
    pane: str
    state: str
    checkpoint: str


@dataclass(frozen=True)
class ResumeDecision:
    active: tuple[PaneRecord, ...]
    quarantine: tuple[PaneRecord, ...]
    strategy: str


def resume_decision(records: list[PaneRecord]) -> ResumeDecision:
    active = tuple(record for record in records if record.state in ACTIVE_STATES)
    quarantine = tuple(record for record in records if record.state in STALE_STATES)
    if not active and quarantine:
        strategy = "launch_recovery_from_latest_checkpoint_and_keep_stale_panes_quarantined"
    elif len(active) == 1:
        strategy = "resume_active_pane"
    elif len(active) > 1:
        strategy = "requires_mainagent_disambiguation_before_resume"
    else:
        strategy = "no_active_or_stale_panes"
    return ResumeDecision(active=active, quarantine=quarantine, strategy=strategy)
