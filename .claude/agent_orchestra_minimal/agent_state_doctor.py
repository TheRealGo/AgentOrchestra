from __future__ import annotations

from pathlib import Path

from .agent_state import AgentState


def finalized_task_file_agent_state_blockers(task_file_path: Path) -> list[str]:
    agents_dir = task_file_path.parent / "agents"
    if not agents_dir.is_dir():
        return []
    blockers: list[str] = []
    for state_file in sorted(agents_dir.glob("*/state.json")):
        agent_id = state_file.parent.name
        try:
            state = AgentState.read(state_file, default_agent_id=agent_id)
        except (OSError, ValueError) as exc:
            blockers.append(f"agent-state:{agent_id}: invalid or unreadable: {exc}")
            continue
        if state.is_main:
            continue
        if state.state != "retired":
            current_id = state.agent_id or agent_id
            blockers.append(f"agent-state:{current_id}: ProfessionalAgent not retired: {state.state}")
    return blockers
