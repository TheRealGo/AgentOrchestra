from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


AgentStateValue = Literal[
    "working",
    "progress",
    "ready",
    "ready_for_review",
    "done",
    "needs_user",
    "blocked",
    "rate_limited",
    "retired",
]

ACTIVE_STATES = frozenset({"working", "progress", "ready"})
QUIET_STATES = frozenset(
    {"ready_for_review", "done", "needs_user", "blocked", "rate_limited", "retired"}
)
KNOWN_STATES = ACTIVE_STATES | QUIET_STATES


@dataclass(frozen=True)
class AgentState:
    state: AgentStateValue
    agent_id: str = ""
    agent_kind: str = "ProfessionalAgent"
    tmux_target: str | None = None

    @classmethod
    def from_mapping(
        cls, data: dict[str, Any], *, default_agent_id: str = ""
    ) -> "AgentState":
        if "state" not in data:
            raise ValueError("agent state mapping must contain state")
        return cls(
            state=_validate_state(str(data["state"]).strip().lower()),
            agent_id=str(data.get("agent_id") or default_agent_id),
            agent_kind=str(data.get("agent_kind") or data.get("kind") or "ProfessionalAgent"),
            tmux_target=_optional_string(data.get("tmux_target") or data.get("pane")),
        )

    @classmethod
    def parse(cls, text: str, *, default_agent_id: str = "") -> "AgentState":
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("agent state file is empty")
        if lines[0].startswith("{"):
            data = json.loads("\n".join(lines))
            if not isinstance(data, dict):
                raise ValueError("agent state JSON must be an object")
            return cls.from_mapping(data, default_agent_id=default_agent_id)
        return cls(state=_validate_state(_state_value(lines)), agent_id=default_agent_id)

    @classmethod
    def read(cls, path: str | Path, *, default_agent_id: str = "") -> "AgentState":
        return cls.parse(Path(path).read_text(encoding="utf-8"), default_agent_id=default_agent_id)

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                {
                    "agent_id": self.agent_id,
                    "agent_kind": self.agent_kind,
                    "state": self.state,
                    "tmux_target": self.tmux_target,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return target

    @property
    def is_main(self) -> bool:
        return self.agent_kind.strip().lower() in {"main", "mainagent", "main_agent"}

    @property
    def is_active(self) -> bool:
        return self.state in ACTIVE_STATES

    @property
    def is_quiet(self) -> bool:
        return self.state in QUIET_STATES


def _state_value(lines: list[str]) -> AgentStateValue:
    if len(lines) == 1:
        return _validate_state(_value_from_line(lines[0]))
    if lines[0] == "[state]" and len(lines) == 2:
        return _validate_state(_value_from_line(lines[1]))
    raise ValueError("agent state must be a single state, state=<value>, JSON object, or [state] block")


def _value_from_line(line: str) -> str:
    if "=" not in line:
        return line.strip().lower()
    key, value = line.split("=", 1)
    if key.strip() != "state":
        raise ValueError(f"invalid agent state key {key.strip()!r}")
    return value.strip().lower()


def _validate_state(value: str) -> AgentStateValue:
    if value not in KNOWN_STATES:
        raise ValueError(f"invalid agent state {value!r}")
    return value  # type: ignore[return-value]


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
