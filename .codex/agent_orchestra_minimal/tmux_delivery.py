from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from os import getpid
from time import sleep

from .tmux_probe import (
    agent_prompt_started_work_without_probe,
    has_active_marker,
    line_has_agent_message_prompt,
    line_has_clearable_composer_prompt,
    last_probe_index,
    last_prompt_marker_index,
    line_has_prompt_marker,
    looks_blocked_by_input_choice,
    looks_interrupted_or_paused,
    looks_recoverable_startup_notice,
    looks_queued,
    looks_recoverable_choice_menu,
    looks_started,
    looks_usage_limited,
    same_ready_prompt_started_work,
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
    clear_default_composer: bool = True,
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
        raise ValueError(f"poll_interval_seconds must be at most {MAX_POLL_INTERVAL_SECONDS}")
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
                submit_key=submit_key,
            )
            if not _pane_is_ready_for_input(baseline_capture):
                return DeliveryResult(False, 0, _tail(baseline_capture))
            baseline_lines = baseline_capture.splitlines()
            baseline_probe_index = last_probe_index(baseline_lines, text)
            baseline_prompt_index = last_prompt_marker_index(baseline_lines)
            if clear_default_composer and _has_clearable_composer_prompt(baseline_lines):
                run(["tmux", "send-keys", "-t", pane_target, "Escape", "C-u"],
                    check=False)
                baseline_capture = _capture(run, pane_target)
                baseline_lines = baseline_capture.splitlines()
                baseline_probe_index = last_probe_index(baseline_lines, text)
                baseline_prompt_index = last_prompt_marker_index(baseline_lines)
        run(["tmux", "paste-buffer", "-t", pane_target, "-b", buffer_name], check=True)
        attempts = 0
        capture = ""
        fresh_probe_was_seen = False
        for attempts in range(1, max_retries + 2):
            run(["tmux", "send-keys", "-t", pane_target,
                 _submit_key_for_attempt(submit_key, attempts)], check=True)
            for poll_index in range(polls_per_attempt):
                capture = _capture(run, pane_target)
                if last_probe_index(capture.splitlines(), text) > baseline_probe_index:
                    fresh_probe_was_seen = True
                state = _delivery_state(
                    capture,
                    text,
                    baseline_capture=baseline_capture if require_fresh_capture else "",
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


def _submit_key_for_attempt(submit_key: str, attempt: int) -> str:
    if attempt % 2 == 1:
        return submit_key
    return _alternate_submit_key(submit_key)


def _alternate_submit_key(submit_key: str) -> str:
    if submit_key == "C-m":
        return "C-j"
    if submit_key == "C-j":
        return "C-m"
    return submit_key


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
    submit_key: str,
) -> str:
    capture = ""
    startup_submit_sent = False
    startup_escape_sent = False
    choice_escape_sent = False
    for poll_index in range(polls):
        capture = _capture(run, pane_target)
        if _pane_is_ready_for_input(capture):
            return capture
        if looks_recoverable_choice_menu(capture) and not choice_escape_sent:
            run(["tmux", "send-keys", "-t", pane_target, "Escape"], check=False)
            choice_escape_sent = True
        if looks_recoverable_startup_notice(capture):
            if not startup_submit_sent:
                run(["tmux", "send-keys", "-t", pane_target, submit_key], check=False)
                startup_submit_sent = True
            elif not startup_escape_sent:
                run(["tmux", "send-keys", "-t", pane_target, "Escape"], check=False)
                startup_escape_sent = True
        if poll_interval_seconds > 0 and poll_index < polls - 1:
            sleep(poll_interval_seconds)
    return capture


def _pane_is_ready_for_input(capture: str) -> bool:
    if looks_usage_limited(capture):
        return False
    if looks_interrupted_or_paused(capture):
        return False
    if looks_blocked_by_input_choice(capture):
        return False
    if looks_recoverable_startup_notice(capture) and last_prompt_marker_index(capture.splitlines()) == -1:
        return False
    lines = capture.splitlines()
    if (prompt_index := last_prompt_marker_index(lines)) == -1:
        return False
    if line_has_agent_message_prompt(lines[prompt_index]):
        return False
    if line_has_prompt_marker(lines[prompt_index]) and has_active_marker(lines[:prompt_index]):
        return False
    tail = "\n".join(lines[prompt_index + 1 :])
    return not looks_queued(tail) and not looks_started(tail)


def _has_clearable_composer_prompt(lines: list[str]) -> bool:
    prompt_index = last_prompt_marker_index(lines)
    return prompt_index != -1 and line_has_clearable_composer_prompt(lines[prompt_index])


def _delivery_state(
    capture: str,
    text: str,
    *,
    baseline_capture: str = "",
    baseline_probe_index: int = -1,
    baseline_prompt_index: int = -1,
    fresh_probe_was_seen: bool = False,
) -> str:
    lines = capture.splitlines()
    blocked_by_input_choice = looks_blocked_by_input_choice(capture)
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
    if blocked_by_input_choice and not fresh_probe_was_seen:
        return "queued"
    prompt_index = last_prompt_marker_index(lines)
    if prompt_index != -1:
        tail = "\n".join(lines[prompt_index + 1 :])
        if looks_queued(tail):
            return "queued"
        if capture == baseline_capture:
            return "uncertain"
        if same_ready_prompt_started_work(
            lines,
            prompt_index,
            tail,
            baseline_capture=baseline_capture,
            baseline_prompt_index=baseline_prompt_index,
        ):
            return "started"
        if agent_prompt_started_work_without_probe(
            lines,
            prompt_index,
            text,
            tail,
            baseline_capture=baseline_capture,
        ):
            return "started"
        if fresh_probe_was_seen and not looks_queued(capture) and looks_started(capture):
            return "started"
        if baseline_prompt_index != -1 and prompt_index > baseline_prompt_index and looks_started(tail):
            return "started"
        return "uncertain"
    if looks_queued(capture):
        return "queued"
    if fresh_probe_was_seen and looks_started(capture):
        return "started"
    return "uncertain"

def _tail(text: str) -> str:
    return "\n".join(text.splitlines()[-40:])
