from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping
from os import getpid
from pathlib import Path
from time import sleep

from .agent_state import AgentState
from .agent_state_doctor import finalized_task_file_agent_state_blockers
from .rekick import WakeDecision, decide_wake
from .task_file import SharedTaskFile
from .tmux_delivery import DEFAULT_SUBMIT_KEY, DeliveryResult, Runner, normalize_submit_key
from .tmux_targets import optional_tmux_pane, required_tmux_pane


WAKE_PAYLOAD = "runtime_wake\nsource=hook\nuser_instruction=false"
WAKE_BUFFER_PREFIX = "agent-orchestra-wake"
# The Stop Hook runs while Claude Code is still blocked on that same hook, so a
# poll-and-confirm send would deadlock (the agent cannot start until the hook
# returns). Instead the wake is a fire-and-forget paste plus several submit-key
# presses: the keys land in the tmux input queue and Claude Code processes them
# once it returns to its idle composer. This mirrors the proven self-exit
# pattern where the paste arrives but the submit only takes effect after the
# active turn yields back to the TUI.
WAKE_SUBMIT_PRESSES = 3
WAKE_SUBMIT_INTERVAL_SECONDS = 1.0


def send_wake(
    pane_target: str,
    *,
    payload: str = WAKE_PAYLOAD,
    submit_key: str = DEFAULT_SUBMIT_KEY,
    runner: Runner | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> DeliveryResult:
    pane_target = required_tmux_pane(pane_target)
    submit_key = normalize_submit_key(submit_key)
    if not pane_target:
        raise ValueError("pane_target is required")
    run = runner or subprocess.run
    sleep_fn = sleeper or sleep
    buffer_name = f"{WAKE_BUFFER_PREFIX}-{getpid()}"
    run(["tmux", "load-buffer", "-b", buffer_name, "-"], input=payload, text=True, check=True)
    try:
        run(["tmux", "paste-buffer", "-t", pane_target, "-b", buffer_name], check=True)
        for index in range(WAKE_SUBMIT_PRESSES):
            run(["tmux", "send-keys", "-t", pane_target, submit_key], check=True)
            if index < WAKE_SUBMIT_PRESSES - 1:
                sleep_fn(WAKE_SUBMIT_INTERVAL_SECONDS)
        return DeliveryResult(True, WAKE_SUBMIT_PRESSES, "")
    finally:
        run(["tmux", "delete-buffer", "-b", buffer_name], check=False)


def run_stop_hook(
    environ: Mapping[str, str],
    *,
    runner: Runner | None = None,
) -> WakeDecision | None:
    """Mechanical Stop Hook bridge.

    Missing required env produces no action. Missing, unreadable, or invalid
    task/state files preserve liveness when a deterministic launch-provided
    target pane is available.
    """

    task_file = _path(environ.get("AGENT_ORCHESTRA_TASK_FILE"))
    state_file = _path(environ.get("AGENT_ORCHESTRA_AGENT_STATE"))
    pane_target, pane_target_invalid = _optional_env_pane(
        environ.get("AGENT_ORCHESTRA_TMUX_PANE")
    )
    if task_file is None or state_file is None:
        return None
    submit_key = environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", "")
    main_pane_target = _optional_pane(environ.get("AGENT_ORCHESTRA_MAIN_TMUX_PANE"))
    if pane_target_invalid:
        if not main_pane_target:
            return None
        pane_target = None
    state = _read_state(state_file, environ)
    if state is None:
        if pane_target and _agent_kind(environ).strip().lower() in {
            "professionalagent",
            "professional_agent",
            "professional",
        }:
            return _send_wake_decision(
                pane_target,
                reason="invalid_agent_state_or_unreadable",
                submit_key=submit_key,
                runner=runner,
            )
        if main_pane_target:
            return _send_wake_decision(
                main_pane_target,
                reason="invalid_agent_state_or_unreadable_main_fallback",
                submit_key=submit_key,
                runner=runner,
            )
        return None
    if not pane_target and state.is_main and main_pane_target:
        pane_target = main_pane_target
    if not pane_target:
        if main_pane_target and _task_file_is_invalid_or_unreadable(task_file):
            return _send_wake_decision(
                main_pane_target,
                reason="invalid_task_file_or_unreadable_main_fallback",
                submit_key=submit_key,
                runner=runner,
            )
        if main_pane_target and state.is_active:
            return _send_wake_decision(
                main_pane_target,
                reason=f"professional_active_{state.state}_main_fallback",
                submit_key=submit_key,
                runner=runner,
            )
        return None
    if not task_file.is_file():
        return _handle_invalid_task_file(state, pane_target, main_pane_target, submit_key, runner)
    try:
        task = SharedTaskFile.read(task_file)
    except (OSError, ValueError):
        return _handle_invalid_task_file(state, pane_target, main_pane_target, submit_key, runner)
    if state.is_main and task.is_finalized and finalized_task_file_agent_state_blockers(task_file):
        return _send_wake_decision(
            pane_target,
            reason="main_done_with_unretired_professional_agents",
            submit_key=submit_key,
            runner=runner,
        )
    decision = decide_wake(task, state)
    if decision.should_wake:
        return _send_wake_decision(
            pane_target,
            reason=decision.reason,
            submit_key=submit_key,
            runner=runner,
        )
    return decision


def _path(raw: str | None) -> Path | None:
    if not raw:
        return None
    return Path(raw).expanduser()


def _optional_pane(raw: str | None) -> str | None:
    try:
        return optional_tmux_pane(raw)
    except ValueError:
        return None


def _optional_env_pane(raw: str | None) -> tuple[str | None, bool]:
    try:
        return optional_tmux_pane(raw), False
    except ValueError:
        return None, True


def _task_file_is_invalid_or_unreadable(task_file: Path) -> bool:
    if not task_file.is_file():
        return True
    try:
        SharedTaskFile.read(task_file)
    except (OSError, ValueError):
        return True
    return False


def _agent_kind(environ: Mapping[str, str]) -> str:
    return environ.get("AGENT_ORCHESTRA_AGENT_KIND", "")


def _read_state(state_file: Path, environ: Mapping[str, str]) -> AgentState | None:
    try:
        return AgentState.read(
            state_file,
            default_agent_id=environ.get("AGENT_ORCHESTRA_AGENT_ID", ""),
            default_agent_kind=environ.get("AGENT_ORCHESTRA_AGENT_KIND", ""),
        )
    except (OSError, ValueError):
        return _fallback_main_state(environ)


def _fallback_main_state(environ: Mapping[str, str]) -> AgentState | None:
    try:
        fallback = AgentState(
            state="working",
            agent_kind=environ.get("AGENT_ORCHESTRA_AGENT_KIND", ""),
        )
    except ValueError:
        return None
    if fallback.is_main:
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
        return _send_wake_decision(
            pane_target,
            reason="invalid_task_file_or_unreadable",
            submit_key=submit_key,
            runner=runner,
        )
    if main_pane_target:
        return _send_wake_decision(
            main_pane_target,
            reason="invalid_task_file_or_unreadable_main_fallback",
            submit_key=submit_key,
            runner=runner,
        )
    return WakeDecision(False, f"quiet_with_invalid_task_file_{state.state}")


def _send_wake_decision(
    pane_target: str,
    *,
    reason: str,
    submit_key: str,
    runner: Runner | None,
) -> WakeDecision:
    try:
        result = send_wake(pane_target, submit_key=submit_key, runner=runner)
    except (ValueError, OSError, subprocess.CalledProcessError):
        return WakeDecision(True, f"{reason}_wake_delivery_failed")
    if result.accepted:
        return WakeDecision(True, reason)
    return WakeDecision(True, f"{reason}_wake_delivery_unaccepted")
