from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping
from os import getpid
from pathlib import Path

from .agent_state import AgentState
from .rekick import WakeDecision, decide_wake
from .task_file import SharedTaskFile


WAKE_PAYLOAD = "runtime_wake\nsource=hook\nuser_instruction=false"
WAKE_BUFFER_PREFIX = "agent-orchestra-wake"
DEFAULT_SUBMIT_KEY = "C-m"

Runner = Callable[..., subprocess.CompletedProcess[str]]


def send_wake(
    pane_target: str,
    *,
    payload: str = WAKE_PAYLOAD,
    submit_key: str = DEFAULT_SUBMIT_KEY,
    runner: Runner | None = None,
) -> None:
    if not pane_target.strip():
        raise ValueError("pane_target is required")
    if not submit_key.strip():
        raise ValueError("submit_key is required")
    run = runner or subprocess.run
    wake_buffer = f"{WAKE_BUFFER_PREFIX}-{getpid()}"
    run(
        ["tmux", "load-buffer", "-b", wake_buffer, "-"],
        input=payload,
        text=True,
        check=True,
    )
    try:
        run(["tmux", "paste-buffer", "-t", pane_target, "-b", wake_buffer], check=True)
        run(["tmux", "send-keys", "-t", pane_target, submit_key], check=True)
    finally:
        run(["tmux", "delete-buffer", "-b", wake_buffer], check=False)


def run_stop_hook(
    environ: Mapping[str, str],
    *,
    runner: Runner | None = None,
) -> WakeDecision | None:
    """Mechanical Stop Hook bridge.

    Missing required env produces no action. Missing, unreadable, or invalid
    task/state files preserve liveness when a deterministic target pane is
    available.
    """

    task_file = _path(environ.get("AGENT_ORCHESTRA_TASK_FILE"))
    state_file = _path(environ.get("AGENT_ORCHESTRA_AGENT_STATE"))
    pane_target = environ.get("AGENT_ORCHESTRA_TMUX_PANE") or environ.get("TMUX_PANE")
    if task_file is None or state_file is None:
        return None
    submit_key = environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", "").strip() or DEFAULT_SUBMIT_KEY
    main_pane_target = environ.get("AGENT_ORCHESTRA_MAIN_TMUX_PANE")
    state = _read_state(state_file, environ)
    if state is None:
        if main_pane_target:
            send_wake(main_pane_target, submit_key=submit_key, runner=runner)
            return WakeDecision(True, "invalid_agent_state_or_unreadable_main_fallback")
        return None
    if state.tmux_target:
        pane_target = state.tmux_target
    if not pane_target:
        return None
    if not task_file.is_file():
        return _handle_invalid_task_file(state, pane_target, main_pane_target, submit_key, runner)
    try:
        task = SharedTaskFile.read(task_file)
    except (OSError, ValueError):
        return _handle_invalid_task_file(state, pane_target, main_pane_target, submit_key, runner)
    decision = decide_wake(task, state)
    if decision.should_wake:
        send_wake(pane_target, submit_key=submit_key, runner=runner)
    return decision


def _path(raw: str | None) -> Path | None:
    if not raw:
        return None
    return Path(raw).expanduser()


def _read_state(state_file: Path, environ: Mapping[str, str]) -> AgentState | None:
    try:
        return AgentState.read(
            state_file,
            default_agent_id=environ.get("AGENT_ORCHESTRA_AGENT_ID", ""),
        )
    except (OSError, ValueError):
        return _fallback_main_state(environ)


def _fallback_main_state(environ: Mapping[str, str]) -> AgentState | None:
    if AgentState(state="working", agent_kind=environ.get("AGENT_ORCHESTRA_AGENT_KIND", "")).is_main:
        return AgentState(
            state="working",
            agent_id=environ.get("AGENT_ORCHESTRA_AGENT_ID", ""),
            agent_kind="MainAgent",
        )
    return None


def _handle_invalid_task_file(
    state: AgentState,
    pane_target: str,
    main_pane_target: str | None,
    submit_key: str,
    runner: Runner | None,
) -> WakeDecision:
    if state.is_main or state.is_active:
        send_wake(pane_target, submit_key=submit_key, runner=runner)
        return WakeDecision(True, "invalid_task_file_or_unreadable")
    if main_pane_target:
        send_wake(main_pane_target, submit_key=submit_key, runner=runner)
        return WakeDecision(True, "invalid_task_file_or_unreadable_main_fallback")
    return WakeDecision(False, f"quiet_with_invalid_task_file_{state.state}")
