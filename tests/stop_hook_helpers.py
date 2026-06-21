from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.tmux_wake import WAKE_PAYLOAD  # noqa: E402


WAKE_PROMPT = " ".join(WAKE_PAYLOAD.split())


class FakeTmux:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str | None]] = []
        self.capture_count = 0
        self.composer_cleared = False
        self.paste_seen = False

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, kwargs.get("input") if isinstance(kwargs.get("input"), str) else None))
        stdout = ""
        if args[:2] == ["tmux", "send-keys"] and args[-2:] == ["Escape", "C-u"]:
            self.composer_cleared = True
        if args[:2] == ["tmux", "paste-buffer"]:
            self.paste_seen = True
        if len(args) >= 6 and args[:3] == ["tmux", "send-keys", "-t"] and "-l" in args:
            self.paste_seen = True
        if args[:2] == ["tmux", "capture-pane"]:
            self.capture_count += 1
            if self.capture_count == 1:
                stdout = "› Implement {feature}\n"
            elif self.composer_cleared and not self.paste_seen:
                stdout = "› \n"
            else:
                stdout = f"› {WAKE_PROMPT}\n\n• Working\n"
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


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
        "Acceptance": [],
        "Gates": [],
        "Candidates": candidates or [],
        "Done": done or [],
    }
    lines = ["[status]", status, ""]
    for section, items in sections.items():
        lines.append(f"[{section}]")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    return "\n".join(lines)
