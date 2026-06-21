from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from time import sleep

from .tmux_probe import (
    has_active_marker,
    last_prompt_marker_index,
    line_has_agent_message_prompt,
    line_has_prompt_marker,
    looks_blocked_by_input_choice,
    looks_interrupted_or_paused,
    looks_queued,
    looks_recoverable_startup_notice,
    looks_started,
    looks_usage_limited,
)
from .tmux_targets import required_tmux_pane


Runner = subprocess.run
TIMER_PATTERN = re.compile(
    r"\b(?:\d+h\s*)?(?:\d+m\s*)?\d+s\b|\b\d+h\s*\d+m\b|\b\d+m\b"
)
SPINNER_PATTERN = re.compile(r"^[◦•]\s+Working(?:\s*\([^)]*\))?")
STATUS_LINE_MARKERS = (
    "Pursuing goal",
    "esc to interrupt",
    "to view transcript",
)


@dataclass(frozen=True)
class PaneLiveness:
    state: str
    changed: bool
    reason: str
    capture_tail: str

    @property
    def stale_working(self) -> bool:
        return self.state == "working_stale"


def inspect_pane_liveness(
    pane_target: str,
    *,
    runner: Runner | None = None,
    samples: int = 2,
    interval_seconds: float = 1.0,
) -> PaneLiveness:
    pane_target = required_tmux_pane(pane_target)
    if samples < 1:
        raise ValueError("samples must be positive")
    if interval_seconds < 0:
        raise ValueError("interval_seconds must be non-negative")

    run = runner or subprocess.run
    captures: list[str] = []
    for index in range(samples):
        captures.append(capture_pane(run, pane_target))
        if interval_seconds > 0 and index < samples - 1:
            sleep(interval_seconds)

    first = captures[0]
    last = captures[-1]
    state = classify_capture(last)
    changed = normalized_activity_fingerprint(first) != normalized_activity_fingerprint(last)
    if state == "working" and not changed and samples > 1:
        state = "working_stale"
    return PaneLiveness(
        state=state,
        changed=changed,
        reason=liveness_reason(state, changed),
        capture_tail=tail(last),
    )


def capture_pane(run: Runner, pane_target: str) -> str:
    result = run(
        ["tmux", "capture-pane", "-t", pane_target, "-p", "-S", "-120"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout or ""


def classify_capture(capture: str) -> str:
    if looks_usage_limited(capture):
        return "usage_limited"
    if looks_interrupted_or_paused(capture):
        return "interrupted_or_paused"
    if looks_blocked_by_input_choice(capture):
        return "blocked_input_choice"
    if looks_queued(capture):
        return "queued"
    if looks_recoverable_startup_notice(capture):
        return "startup_notice"
    if has_active_marker(capture.splitlines()):
        return "working"
    if _has_prompt(capture):
        return "ready"
    return "unknown"


def normalized_activity_fingerprint(capture: str) -> str:
    lines: list[str] = []
    for raw_line in capture.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _is_status_only_line(line):
            continue
        line = TIMER_PATTERN.sub("<time>", line)
        lines.append(" ".join(line.split()))
    return "\n".join(lines[-80:])


def liveness_reason(state: str, changed: bool) -> str:
    if state == "working_stale":
        return "pane remained visibly Working without substantive output changes"
    if state == "working":
        return "pane is visibly Working and output changed" if changed else "pane is visibly Working"
    if state == "ready":
        return "pane is ready for input"
    if state == "interrupted_or_paused":
        return "pane is interrupted or goal-paused and needs explicit recovery"
    if state == "queued":
        return "pane has queued composer text"
    if state == "blocked_input_choice":
        return "pane is blocked by an input choice"
    if state == "startup_notice":
        return "pane is showing a recoverable startup notice"
    if state == "usage_limited":
        return "pane is usage-limited"
    return "pane state is unknown"


def tail(text: str) -> str:
    return "\n".join(text.splitlines()[-40:])


def _has_prompt(capture: str) -> bool:
    lines = capture.splitlines()
    prompt_index = last_prompt_marker_index(lines)
    if prompt_index == -1 or line_has_agent_message_prompt(lines[prompt_index]):
        return False
    if not line_has_prompt_marker(lines[prompt_index]):
        return False
    tail = "\n".join(lines[prompt_index + 1 :])
    return not looks_queued(tail) and not looks_started(tail)


def _is_status_only_line(line: str) -> bool:
    if SPINNER_PATTERN.match(line):
        return True
    return any(marker in line for marker in STATUS_LINE_MARKERS)
