from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402


class FakeTmux:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str | None]] = []

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")


class RunFiles:
    def __init__(self, *, agent_kind: str, state: str, task_text: str) -> None:
        self.agent_kind = agent_kind
        self.state = state
        self.task_text = task_text
        self._tmp: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> dict[str, str]:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        task_file = root / "tasks.ini"
        state_file = root / "state.json"
        task_file.write_text(self.task_text, encoding="utf-8")
        AgentState(
            state=self.state,  # type: ignore[arg-type]
            agent_id="agent",
            agent_kind=self.agent_kind,
            tmux_target="%7",
        ).write(state_file)
        return {
            "AGENT_ORCHESTRA_TASK_FILE": str(task_file),
            "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
            "AGENT_ORCHESTRA_TMUX_PANE": "%7",
        }

    def __exit__(self, *_exc: object) -> None:
        if self._tmp is not None:
            self._tmp.cleanup()
