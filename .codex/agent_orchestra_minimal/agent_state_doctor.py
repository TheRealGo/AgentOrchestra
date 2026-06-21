from __future__ import annotations

from pathlib import Path

from .agent_state import AgentState


def finalized_task_file_agent_state_blockers(task_file_path: Path) -> list[str]:
    agents_dir = task_file_path.parent / "agents"
    if not agents_dir.is_dir():
        return []
    blockers: list[str] = []
    for agent_dir in sorted(path for path in agents_dir.iterdir() if path.is_dir()):
        agent_id = agent_dir.name
        state_file = agent_dir / "state.json"
        if not state_file.exists():
            if not _looks_like_main_agent_dir(agent_id):
                blockers.append(f"agent-state:{agent_id}: missing state.json")
            continue
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


def _looks_like_main_agent_dir(agent_id: str) -> bool:
    return agent_id.strip().lower() in {"main", "mainagent", "main_agent"}
