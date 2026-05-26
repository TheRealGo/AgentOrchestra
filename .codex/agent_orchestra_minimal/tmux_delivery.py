from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from os import getpid
from time import sleep

from .tmux_targets import required_tmux_pane


DEFAULT_SUBMIT_KEY = "C-m"
TMUX_KEY_TOKEN = re.compile(r"^[A-Za-z0-9_.:+-]+$")
MAX_RETRIES = 10
MAX_POLL_INTERVAL_SECONDS = 2.0
MAX_POLLS_PER_ATTEMPT = 60
MESSAGE_PROBE_CHARS = 120
MIN_MESSAGE_PROBE_CHARS = 56
MAX_WRAPPED_PROBE_LINES = 24
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
            baseline_lines = _capture(run, pane_target).splitlines()
            baseline_probe_index = _last_probe_index(baseline_lines, text)
            baseline_prompt_index = _last_prompt_marker_index(baseline_lines)
        run(["tmux", "paste-buffer", "-t", pane_target, "-b", buffer_name], check=True)
        attempts = 0
        capture = ""
        fresh_probe_was_seen = False
        for attempts in range(1, max_retries + 2):
            run(["tmux", "send-keys", "-t", pane_target, submit_key], check=True)
            for poll_index in range(polls_per_attempt):
                capture = _capture(run, pane_target)
                if _last_probe_index(capture.splitlines(), text) > baseline_probe_index:
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


def _delivery_state(
    capture: str,
    text: str,
    *,
    baseline_probe_index: int = -1,
    baseline_prompt_index: int = -1,
    fresh_probe_was_seen: bool = False,
) -> str:
    lines = capture.splitlines()
    probe_index = _last_probe_index(lines, text)
    if probe_index != -1:
        if probe_index <= baseline_probe_index:
            return "uncertain"
        tail = "\n".join(lines[probe_index + 1 :])
        if _looks_queued(tail):
            return "queued"
        if _looks_started(tail):
            return "started"
        return "queued"
    prompt_index = _last_prompt_marker_index(lines)
    if prompt_index != -1:
        tail = "\n".join(lines[prompt_index + 1 :])
        if _looks_queued(tail):
            return "queued"
        if fresh_probe_was_seen and not _looks_queued(capture):
            return "started"
        if (
            baseline_prompt_index != -1
            and prompt_index > baseline_prompt_index
            and _looks_started(tail)
        ):
            return "started"
        return "uncertain"
    if _looks_queued(capture):
        return "queued"
    return "uncertain"


def _last_probe_index(lines: list[str], text: str) -> int:
    probes = _message_probes(text)
    if not probes:
        return -1
    for index in range(len(lines) - 1, -1, -1):
        stripped = _normalized_wrapped_line_window(lines, index)
        if any(_probe_matches(probe, stripped) for probe in probes):
            return _wrapped_line_window_end(lines, index)
    return -1


def _normalized_wrapped_line_window(lines: list[str], start: int) -> str:
    window = [lines[start]]
    for line in lines[start + 1 : start + MAX_WRAPPED_PROBE_LINES]:
        if not line[:1].isspace() or _line_has_queue_marker(line):
            break
        window.append(line)
    return " ".join(" ".join(line.strip().split()) for line in window)


def _wrapped_line_window_end(lines: list[str], start: int) -> int:
    end = start
    for index, line in enumerate(lines[start + 1 : start + MAX_WRAPPED_PROBE_LINES], start + 1):
        if not line[:1].isspace() or _line_has_queue_marker(line):
            break
        end = index
    return end


def _last_prompt_marker_index(lines: list[str]) -> int:
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].lstrip().startswith(("›", ">")):
            return index
    return -1


def _looks_started(capture: str) -> bool:
    markers = (
        "• ",
        "Working",
        "Pursuing goal",
        "Explored",
        "Ran ",
        "Edited ",
        "Waiting for",
        "Finished waiting",
    )
    return any(_line_has_start_marker(line, markers) for line in capture.splitlines())


def _line_has_start_marker(line: str, markers: tuple[str, ...]) -> bool:
    if line[:1].isspace():
        return False
    return any(line.startswith(marker) for marker in markers)


def _looks_queued(capture: str) -> bool:
    return any(_line_has_queue_marker(line) for line in capture.splitlines())


def _line_has_queue_marker(line: str) -> bool:
    markers = (
        "tab to queue message",
        "Messages to be submitted after next tool call",
    )
    return any(marker in line for marker in markers)


def _message_probes(text: str) -> tuple[str, ...]:
    normalized = " ".join(text.strip().split())
    first_line = " ".join(text.strip().splitlines()[0].split()) if text.strip() else ""
    probes = []
    for source in (normalized, first_line):
        for length in (MESSAGE_PROBE_CHARS, 80, MIN_MESSAGE_PROBE_CHARS):
            candidate = source[:length]
            if candidate and (len(source) <= length or len(candidate) >= MIN_MESSAGE_PROBE_CHARS):
                if candidate not in probes:
                    probes.append(candidate)
    return tuple(probes)


def _probe_matches(probe: str, capture_window: str) -> bool:
    if probe in capture_window:
        return True
    if not _has_non_ascii(probe):
        return False
    return _without_whitespace(probe) in _without_whitespace(capture_window)


def _has_non_ascii(text: str) -> bool:
    return any(ord(character) > 127 for character in text)


def _without_whitespace(text: str) -> str:
    return "".join(text.split())


def _tail(text: str) -> str:
    return "\n".join(text.splitlines()[-40:])
