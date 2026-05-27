from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from os import getpid
from time import sleep

from .tmux_probe import (
    line_has_agent_message_prompt,
    last_probe_index,
    last_prompt_marker_index,
    line_has_prompt_marker,
    line_has_start_marker,
    looks_queued,
    looks_started,
)
from .tmux_targets import required_tmux_pane


DEFAULT_SUBMIT_KEY = "C-m"
TMUX_KEY_TOKEN = re.compile(r"^[A-Za-z0-9_.:+-]+$")
MAX_RETRIES = 10
MAX_POLL_INTERVAL_SECONDS = 2.0
MAX_POLLS_PER_ATTEMPT = 60
Runner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class DeliveryResult:
    accepted: bool
    attempts: int
    capture_tail: str


def send_buffered_text(
    pane_target: str,
    text: str,
    *,
    buffer_prefix: str,
    submit_key: str = DEFAULT_SUBMIT_KEY,
    runner: Runner | None = None,
    max_retries: int = 2,
    poll_interval_seconds: float = 0.2,
    polls_per_attempt: int = 1,
    require_fresh_capture: bool = True,
) -> DeliveryResult:
    pane_target = required_tmux_pane(pane_target)
    submit_key = normalize_submit_key(submit_key)
    if not pane_target:
        raise ValueError("pane_target is required")
    if not text.strip():
        raise ValueError("text is required")
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    if max_retries > MAX_RETRIES:
        raise ValueError(f"max_retries must be at most {MAX_RETRIES}")
    if poll_interval_seconds < 0:
        raise ValueError("poll_interval_seconds must be non-negative")
    if poll_interval_seconds > MAX_POLL_INTERVAL_SECONDS:
        raise ValueError(
            f"poll_interval_seconds must be at most {MAX_POLL_INTERVAL_SECONDS}"
        )
    if polls_per_attempt < 1:
        raise ValueError("polls_per_attempt must be positive")
    if polls_per_attempt > MAX_POLLS_PER_ATTEMPT:
        raise ValueError(f"polls_per_attempt must be at most {MAX_POLLS_PER_ATTEMPT}")

    run = runner or subprocess.run
    buffer_name = f"{buffer_prefix}-{getpid()}"
    run(["tmux", "load-buffer", "-b", buffer_name, "-"], input=text, text=True, check=True)
    try:
        baseline_probe_index = -1
        baseline_prompt_index = -1
        if require_fresh_capture:
            baseline_capture = _wait_for_ready_input(
                run,
                pane_target,
                poll_interval_seconds=poll_interval_seconds,
                polls=polls_per_attempt,
            )
            if not _pane_is_ready_for_input(baseline_capture):
                return DeliveryResult(False, 0, _tail(baseline_capture))
            baseline_lines = baseline_capture.splitlines()
            baseline_probe_index = last_probe_index(baseline_lines, text)
            baseline_prompt_index = last_prompt_marker_index(baseline_lines)
        run(["tmux", "paste-buffer", "-t", pane_target, "-b", buffer_name], check=True)
        attempts = 0
        capture = ""
        fresh_probe_was_seen = False
        for attempts in range(1, max_retries + 2):
            run(["tmux", "send-keys", "-t", pane_target, submit_key], check=True)
            for poll_index in range(polls_per_attempt):
                capture = _capture(run, pane_target)
                if last_probe_index(capture.splitlines(), text) > baseline_probe_index:
                    fresh_probe_was_seen = True
                state = _delivery_state(
                    capture,
                    text,
                    baseline_probe_index=baseline_probe_index,
                    baseline_prompt_index=baseline_prompt_index,
                    fresh_probe_was_seen=fresh_probe_was_seen,
                )
                if state == "started":
                    return DeliveryResult(True, attempts, _tail(capture))
                if poll_interval_seconds > 0 and poll_index < polls_per_attempt - 1:
                    sleep(poll_interval_seconds)
        return DeliveryResult(False, attempts, _tail(capture))
    finally:
        run(["tmux", "delete-buffer", "-b", buffer_name], check=False)


def normalize_submit_key(value: str | None) -> str:
    key = (value or "").strip() or DEFAULT_SUBMIT_KEY
    if not TMUX_KEY_TOKEN.fullmatch(key):
        raise ValueError("submit_key must be a single tmux key token")
    return key


def _capture(run: Runner, pane_target: str) -> str:
    result = run(
        ["tmux", "capture-pane", "-t", pane_target, "-p", "-S", "-120"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout or ""


def _wait_for_ready_input(
    run: Runner,
    pane_target: str,
    *,
    poll_interval_seconds: float,
    polls: int,
) -> str:
    capture = ""
    for poll_index in range(polls):
        capture = _capture(run, pane_target)
        if _pane_is_ready_for_input(capture):
            return capture
        if poll_interval_seconds > 0 and poll_index < polls - 1:
            sleep(poll_interval_seconds)
    return capture


def _pane_is_ready_for_input(capture: str) -> bool:
    lines = capture.splitlines()
    if (prompt_index := last_prompt_marker_index(lines)) == -1:
        return False
    if line_has_agent_message_prompt(lines[prompt_index]):
        return False
    if line_has_prompt_marker(lines[prompt_index]) and _has_active_marker(lines[:prompt_index]):
        return False
    tail = "\n".join(lines[prompt_index + 1 :])
    return not looks_queued(tail) and not looks_started(tail)


def _delivery_state(
    capture: str,
    text: str,
    *,
    baseline_probe_index: int = -1,
    baseline_prompt_index: int = -1,
    fresh_probe_was_seen: bool = False,
) -> str:
    lines = capture.splitlines()
    probe_index = last_probe_index(lines, text)
    if probe_index != -1:
        if probe_index <= baseline_probe_index:
            return "uncertain"
        tail = "\n".join(lines[probe_index + 1 :])
        if looks_queued(tail):
            return "queued"
        if looks_started(tail):
            return "started"
        return "queued"
    prompt_index = last_prompt_marker_index(lines)
    if prompt_index != -1:
        tail = "\n".join(lines[prompt_index + 1 :])
        if looks_queued(tail):
            return "queued"
        if fresh_probe_was_seen and not looks_queued(capture):
            return "started"
        if (
            baseline_prompt_index != -1
            and prompt_index > baseline_prompt_index
            and looks_started(tail)
        ):
            return "started"
        return "uncertain"
    if looks_queued(capture):
        return "queued"
    return "uncertain"


def _has_active_marker(lines: list[str]) -> bool:
    active_markers = ("• Working", "Working", "Pursuing goal")
    done_markers = ("Done.", "Done", "FAILED", "Failed", "Cancelled", "─ Worked for")
    return max(
        (i for i, line in enumerate(lines) if line_has_start_marker(line, active_markers)),
        default=-1,
    ) > max(
        (i for i, line in enumerate(lines) if line_has_start_marker(line, done_markers)),
        default=-1,
    )


def _tail(text: str) -> str:
    return "\n".join(text.splitlines()[-40:])
