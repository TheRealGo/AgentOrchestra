from __future__ import annotations
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from time import sleep
from .tmux_probe import agent_prompt_started_work_without_probe, has_active_marker, line_has_agent_message_prompt
from .tmux_probe import line_has_clearable_composer_prompt, line_has_default_composer_prompt, line_has_prompt_marker
from .tmux_probe import last_probe_index, last_prompt_marker_index, looks_blocked_by_input_choice
from .tmux_probe import looks_interrupted_or_paused, looks_queued, looks_queued_before_started
from .tmux_probe import looks_recoverable_choice_menu, looks_recoverable_startup_notice, looks_started
from .tmux_probe import looks_startup_in_progress, looks_usage_limited, normalized_wrapped_line_window
from .tmux_probe import same_ready_prompt_started_work
from .tmux_delivery_markers import has_new_marker_line
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
    allow_interrupted_recovery: bool = False,
) -> DeliveryResult:
    pane_target = required_tmux_pane(pane_target)
    submit_key = normalize_submit_key(submit_key)
    if not pane_target:
        raise ValueError("pane_target is required")
    if not text.strip():
        raise ValueError("text is required")
    text = " ".join(text.strip().split())
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
    baseline_probe_index = -1
    baseline_prompt_index = -1
    if require_fresh_capture:
        baseline_capture = _wait_for_ready_input(
            run,
            pane_target,
            poll_interval_seconds=poll_interval_seconds,
            polls=polls_per_attempt,
            submit_key=submit_key,
            allow_interrupted_recovery=allow_interrupted_recovery,
        )
        if not _pane_is_ready_for_input(
            baseline_capture,
            allow_interrupted_recovery=allow_interrupted_recovery,
        ):
            return DeliveryResult(False, 0, _tail(baseline_capture))
        baseline_lines = baseline_capture.splitlines()
        baseline_probe_index = last_probe_index(baseline_lines, text)
        baseline_prompt_index = last_prompt_marker_index(baseline_lines)
        for _ in range(3 if clear_default_composer else 0):
            if not _has_clearable_composer_prompt(baseline_lines):
                break
            previous_capture = baseline_capture
            run(["tmux", "send-keys", "-t", pane_target, "Escape", "C-u"], check=False); sleep(0.2)
            baseline_capture = _capture(run, pane_target)
            baseline_lines = baseline_capture.splitlines()
            baseline_probe_index = last_probe_index(baseline_lines, text)
            baseline_prompt_index = last_prompt_marker_index(baseline_lines)
            if baseline_capture == previous_capture:
                break
    _paste_text(run, pane_target, text, buffer_prefix=buffer_prefix)
    paste_capture = _wait_for_pasted_text(run, pane_target, text, baseline_probe_index, min(poll_interval_seconds, 0.2), polls_per_attempt)
    attempts = 0
    capture = ""
    fresh_probe_was_seen = last_probe_index(paste_capture.splitlines(), text) > baseline_probe_index
    for attempts in range(1, max_retries + 2):
        run(["tmux", "send-keys", "-t", pane_target, _submit_key_for_attempt(submit_key, attempts)], check=True)
        for poll_index in range(polls_per_attempt):
            capture = _capture(run, pane_target)
            if not capture and paste_capture and looks_started(paste_capture):
                capture = paste_capture
                paste_capture = ""
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
def normalize_submit_key(value: str | None) -> str:
    key = (value or "").strip() or DEFAULT_SUBMIT_KEY
    if not TMUX_KEY_TOKEN.fullmatch(key):
        raise ValueError("submit_key must be a single tmux key token")
    return key
def _submit_key_for_attempt(submit_key: str, attempt: int) -> str:
    return submit_key if attempt % 2 == 1 else _alternate_submit_key(submit_key)
def _alternate_submit_key(submit_key: str) -> str:
    if submit_key == "C-m":
        return "C-j"
    if submit_key == "C-j":
        return "C-m"
    return "C-m"
def _capture(run: Runner, pane_target: str) -> str:
    result = run(
        ["tmux", "capture-pane", "-t", pane_target, "-p", "-S", "-120"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout or ""
def _paste_text(run: Runner, pane_target: str, text: str, *, buffer_prefix: str) -> None:
    buffer_name = f"{buffer_prefix}-{pane_target.lstrip('%')}"
    try:
        run(["tmux", "load-buffer", "-b", buffer_name, "-"], check=True, text=True, input=text); run(["tmux", "paste-buffer", "-t", pane_target, "-b", buffer_name], check=True)
    finally:
        run(["tmux", "delete-buffer", "-b", buffer_name], check=False)
def _wait_for_pasted_text(run: Runner, pane_target: str, text: str, baseline_probe_index: int, poll_interval_seconds: float, polls: int) -> str:
    capture = ""
    for poll_index in range(polls):
        capture = _capture(run, pane_target)
        if last_probe_index(capture.splitlines(), text) > baseline_probe_index:
            return capture
        if poll_interval_seconds > 0 and poll_index < polls - 1:
            sleep(poll_interval_seconds)
    return capture
def _wait_for_ready_input(
    run: Runner,
    pane_target: str,
    *,
    poll_interval_seconds: float,
    polls: int,
    submit_key: str,
    allow_interrupted_recovery: bool = False,
) -> str:
    capture = ""
    startup_submit_sent = False
    startup_escape_sent = False
    choice_escape_sent = False
    for poll_index in range(polls):
        capture = _capture(run, pane_target)
        if looks_startup_in_progress(capture) and not startup_escape_sent and not has_active_marker(capture.splitlines()): run(["tmux", "send-keys", "-t", pane_target, "Escape"], check=False); startup_escape_sent = True
        if _pane_is_ready_for_input(capture, allow_interrupted_recovery=allow_interrupted_recovery):
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
def _pane_is_ready_for_input(capture: str, *, allow_interrupted_recovery: bool = False) -> bool:
    if looks_usage_limited(capture):
        return False
    if looks_interrupted_or_paused(capture):
        if allow_interrupted_recovery:
            return True
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
    if line_has_prompt_marker(lines[prompt_index]) and _has_active_marker_since_last_separator(lines, prompt_index):
        return False
    tail = "\n".join(lines[prompt_index + 1 :])
    return not looks_queued(tail) and not looks_started(tail)
def _has_clearable_composer_prompt(lines: list[str]) -> bool:
    prompt_index = last_prompt_marker_index(lines)
    if prompt_index == -1:
        return False
    if line_has_clearable_composer_prompt(lines[prompt_index]):
        return True
    if not line_has_prompt_marker(lines[prompt_index]):
        return False
    tail = lines[prompt_index + 1 :]
    return all(not line.strip() for line in tail)
def _has_active_marker_since_last_separator(lines: list[str], prompt_index: int) -> bool:
    for index in range(prompt_index - 1, -1, -1):
        if lines[index].strip().startswith("─"):
            return has_active_marker(lines[index + 1 : prompt_index])
    return has_active_marker(lines[:prompt_index])
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
        if _has_prior_fragment_prompt(lines, text, baseline_prompt_index, probe_index):
            return "queued"
        prompt_index = last_prompt_marker_index(lines)
        if prompt_index > probe_index and line_has_clearable_composer_prompt(lines[prompt_index]):
            tail_after_prompt = "\n".join(lines[prompt_index + 1 :])
            if not line_has_default_composer_prompt(lines[prompt_index]) and not looks_started(tail_after_prompt):
                return "queued"
        tail = "\n".join(lines[probe_index + 1 :])
        if looks_queued_before_started(tail):
            return "queued"
        if looks_started(tail):
            return "started"
        if looks_queued(tail):
            return "queued"
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
        if same_ready_prompt_started_work(lines, prompt_index, tail, baseline_capture=baseline_capture, baseline_prompt_index=baseline_prompt_index):
            return "started"
        if agent_prompt_started_work_without_probe(lines, prompt_index, text, tail, baseline_capture=baseline_capture):
            return "started"
        if fresh_probe_was_seen and not looks_queued(capture) and looks_started(capture):
            return "started"
        if (
            baseline_capture
            and capture != baseline_capture
            and baseline_prompt_index != -1
            and not looks_queued_before_started(capture)
            and (fresh_probe_was_seen or _has_new_agent_acknowledgement(capture, baseline_capture))
            and _has_new_substantive_activity(capture, baseline_capture)
        ):
            return "started"
        if fresh_probe_was_seen and baseline_prompt_index != -1 and prompt_index > baseline_prompt_index and looks_started(tail):
            return "started"
        return "uncertain"
    if looks_queued(capture):
        return "queued"
    if (
        baseline_capture
        and capture != baseline_capture
        and _has_new_agent_acknowledgement(capture, baseline_capture)
        and _has_new_substantive_activity(capture, baseline_capture)
    ):
        return "started"
    if fresh_probe_was_seen and looks_started(capture):
        return "started"
    return "uncertain"
def _tail(text: str) -> str:
    return "\n".join(text.splitlines()[-40:])
def _has_prior_fragment_prompt(lines: list[str], text: str, baseline_prompt_index: int, probe_index: int) -> bool:
    return any(i > baseline_prompt_index and i < probe_index and line_has_clearable_composer_prompt(lines[i]) and normalized_wrapped_line_window(lines, i).lstrip("›> ") in text for i in range(len(lines)))
def _has_new_substantive_activity(capture: str, baseline_capture: str) -> bool:
    markers = ("• I", "• Ran ", "• Edited ", "• Explored", "Ran ", "Edited ", "Explored ")
    return has_new_marker_line(capture, baseline_capture, markers)
def _has_new_agent_acknowledgement(capture: str, baseline_capture: str) -> bool:
    markers = ("• I'll ", "• I’ll ", "• I will ", "• I can ", "• I’m ", "• I'm ", "• Using ")
    return has_new_marker_line(capture, baseline_capture, markers)
