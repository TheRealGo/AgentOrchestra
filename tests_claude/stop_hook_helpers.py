from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402


class FakeTmux:
    """Record tmux calls for the Claude Code fire-and-forget wake.

    The Claude Code ``send_wake`` does not poll/capture (it would deadlock on
    its own Stop Hook), so unlike the Codex fake there is no capture-pane
    confirmation behavior to model: every command simply succeeds.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str | None]] = []

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")


class NoWakeSleepMixin:
    """Patch the wake submit-key interval sleep so ``run_stop_hook`` tests are fast.

    ``run_stop_hook`` calls ``send_wake`` without a ``sleeper`` injection point,
    so the module-level ``sleep`` (the real ``time.sleep``) is replaced for the
    duration of each test. This only removes the 1s spacing between the fixed
    submit-key presses; it does not change which tmux commands are issued.
    """

    def setUp(self) -> None:
        super().setUp()
        patcher = mock.patch("agent_orchestra_minimal.tmux_wake.sleep", lambda *_args: None)
        patcher.start()
        self.addCleanup(patcher.stop)


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


def task_text(
    *,
    status: str,
    backlog: list[str] | None = None,
    in_progress: list[str] | None = None,
    in_review: list[str] | None = None,
    candidates: list[str] | None = None,
    done: list[str] | None = None,
) -> str:
    sections = {
        "Backlog": backlog or [],
        "InProgress": in_progress or [],
        "InReview": in_review or [],
        "Candidates": candidates or [],
        "Done": done or [],
    }
    lines = ["[status]", status, ""]
    for section, items in sections.items():
        lines.append(f"[{section}]")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    return "\n".join(lines)
