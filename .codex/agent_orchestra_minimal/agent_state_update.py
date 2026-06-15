from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .agent_state import AgentState


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="update an AgentOrchestra agent state file canonically")
    parser.add_argument("--state-file", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--agent-id")
    parser.add_argument("--agent-kind")
    parser.add_argument("--tmux-target")
    args = parser.parse_args(argv)

    path = Path(args.state_file)
    existing: AgentState | None = None
    if path.exists():
        existing = AgentState.read(path)

    AgentState(
        state=args.state,  # type: ignore[arg-type]
        agent_id=args.agent_id or (existing.agent_id if existing else ""),
        agent_kind=args.agent_kind or (existing.agent_kind if existing else "ProfessionalAgent"),
        tmux_target=args.tmux_target if args.tmux_target is not None else (existing.tmux_target if existing else None),
    ).write(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
