from __future__ import annotations

from dataclasses import dataclass

from .agent_state import AgentState
from .task_file import SharedTaskFile


@dataclass(frozen=True)
class WakeDecision:
    should_wake: bool
    reason: str


def decide_wake(task_file: SharedTaskFile, agent_state: AgentState) -> WakeDecision:
    """Return the deterministic Stop Hook wake decision."""

    if agent_state.is_main:
        if task_file.is_finalized:
            return WakeDecision(False, "main_done_without_open_work")
        if task_file.status == "progress":
            return WakeDecision(True, "main_status_progress")
        if task_file.status == "done" and task_file.has_open_work:
            return WakeDecision(True, "main_done_with_open_work")
        if task_file.status == "done" and task_file.has_unresolved_candidates:
            return WakeDecision(True, "main_done_with_unresolved_candidates")
        return WakeDecision(True, "main_has_finalization_blockers")

    if agent_state.is_active:
        return WakeDecision(True, f"professional_active_{agent_state.state}")
    return WakeDecision(False, f"professional_quiet_{agent_state.state}")
