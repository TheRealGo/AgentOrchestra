from __future__ import annotations
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from agent_orchestra_minimal.self_exit_session import cleanup_auxiliary_shell_panes
    from agent_orchestra_minimal.tmux_delivery import normalize_submit_key
    from agent_orchestra_minimal.tmux_targets import required_tmux_pane
else:
    from .self_exit_session import cleanup_auxiliary_shell_panes
    from .tmux_delivery import normalize_submit_key
    from .tmux_targets import required_tmux_pane
Runner = Callable[..., subprocess.CompletedProcess[str]]
Sleeper = Callable[[float], None]
CODEX_PANE_COMMANDS = frozenset({"codex", "node"})
SHELL_PANE_COMMANDS = frozenset({"bash", "zsh", "sh", "fish"})
SELF_E2E_SESSION_PREFIX = "AgentOrchestra-self-e2e-"
MEMORY_PROMPT_MARKERS = ("› [ ] Memories", "Press space to select or enter to save")
@dataclass(frozen=True)
class SelfExitResult:
    closed: bool
    attempts: int
    cleared_leftover: bool
    killed_pane: bool
    reason: str
    pane: str
    session_name: str = ""
    auxiliary_shell_panes: tuple[str, ...] = ()
    session_gone: bool = False
def run_self_exit(
    pane: str,
    *,
    submit_key: str,
    runner: Runner | None = None,
    sleeper: Sleeper = time.sleep,
    attempts: int = 4,
    delay_seconds: float = 2.0,
    allow_shell_cleanup_session_prefix: str | None = None,
    cleanup_auxiliary_shells: bool = False,
) -> SelfExitResult:
    pane = required_tmux_pane(pane)
    submit_key = normalize_submit_key(submit_key)
    if attempts < 1:
        raise ValueError("attempts must be positive")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be non-negative")
    run = runner or subprocess.run
    sent = 0
    for attempt in range(1, attempts + 1):
        if delay_seconds:
            sleeper(delay_seconds)
        if not _pane_exists(run, pane):
            return SelfExitResult(True, sent, False, False, "pane_closed", pane)
        pane_command = _pane_command(run, pane)
        session_name = _pane_session(run, pane)
        if pane_command not in CODEX_PANE_COMMANDS:
            if _shell_cleanup_is_authorized(
                pane_command,
                session_name,
                allow_shell_cleanup_session_prefix,
            ):
                cleared = _clear_queued_exit(run, pane)
                killed = _kill_shell_cleanup_target(run, pane, session_name)
                closed = killed and not _pane_exists(run, pane)
                aux = cleanup_auxiliary_shell_panes(
                    run, session_name=session_name, session_prefix=allow_shell_cleanup_session_prefix, exclude_pane=pane
                ) if cleanup_auxiliary_shells else ()
                session_gone = _session_gone(run, session_name) if session_name else False
                return SelfExitResult(
                    closed,
                    sent,
                    cleared,
                    killed,
                    "dedicated_session_shell_cleanup" if closed else "pane_not_codex_cleanup_failed",
                    pane,
                    session_name,
                    aux,
                    session_gone,
                )
            return SelfExitResult(False, sent, False, False, "pane_not_codex", pane, session_name)
        if _looks_memory_prompt(_capture(run, pane)):
            _send_keys(run, pane, _submit_key_for_attempt(submit_key, attempt))
            if delay_seconds:
                sleeper(delay_seconds)
            if not _pane_exists(run, pane):
                session_gone = _session_gone(run, session_name) if session_name else False
                return SelfExitResult(
                    True,
                    sent,
                    False,
                    False,
                    "memory_prompt_closed_after_submit",
                    pane,
                    session_name,
                    (),
                    session_gone,
                )
            continue
        _send_keys(run, pane, "Escape", "C-u")
        if delay_seconds:
            sleeper(min(delay_seconds, 0.2))
        _send_keys(run, pane, "/exit", _submit_key_for_attempt(submit_key, attempt))
        sent += 1
        if delay_seconds:
            sleeper(delay_seconds)
        if not _pane_exists(run, pane):
            session_gone = _session_gone(run, session_name) if session_name else False
            aux = cleanup_auxiliary_shell_panes(
                run, session_name=session_name, session_prefix=allow_shell_cleanup_session_prefix, exclude_pane=pane
            ) if cleanup_auxiliary_shells else ()
            session_gone = _session_gone(run, session_name) if session_name else session_gone
            return SelfExitResult(True, sent, False, False, "pane_closed", pane, session_name, aux, session_gone)
    final_session_name = _pane_session(run, pane)
    final_command = _pane_command(run, pane)
    if not _forced_kill_cleanup_is_authorized(final_session_name, allow_shell_cleanup_session_prefix):
        cleared = _clear_queued_exit(run, pane)
        return SelfExitResult(
            False,
            sent,
            cleared,
            False,
            "pane_session_mismatch_after_exit_attempt",
            pane,
            final_session_name,
        )
    cleared = _clear_queued_exit(run, pane)
    killed = _kill_pane_cleanup(run, pane)
    closed = killed and not _pane_exists(run, pane)
    aux = cleanup_auxiliary_shell_panes(
        run, session_name=final_session_name, session_prefix=allow_shell_cleanup_session_prefix, exclude_pane=pane
    ) if cleanup_auxiliary_shells else ()
    session_gone = _session_gone(run, final_session_name) if final_session_name else False
    return SelfExitResult(
        closed,
        sent,
        cleared,
        killed,
        "shell_after_exit_cleanup" if closed and final_command in SHELL_PANE_COMMANDS else "kill_pane_cleanup_after_exit_attempt" if closed else "pane_still_present",
        pane,
        final_session_name,
        aux,
        session_gone,
    )
def resolve_pane() -> str:
    pane = os.environ.get("AGENT_ORCHESTRA_TMUX_PANE", "").strip()
    if pane:
        return pane
    candidates: list[Path] = []
    if os.environ.get("AGENT_ORCHESTRA_AGENT_STATE"):
        candidates.append(Path(os.environ["AGENT_ORCHESTRA_AGENT_STATE"]))
    if os.environ.get("CODEX_HOME"):
        candidates.append(Path(os.environ["CODEX_HOME"]).parent / "state.json")
    for path in candidates:
        try:
            candidate = json.loads(path.read_text(encoding="utf-8")).get("tmux_target", "").strip()
        except (OSError, json.JSONDecodeError):
            continue
        if candidate:
            return candidate
    raise SystemExit("cannot resolve MainAgent tmux pane for self-exit")
def _pane_exists(run: Runner, pane: str) -> bool:
    result = run(
        ["tmux", "list-panes", "-a", "-F", "#{pane_id}"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return False
    return pane in set((result.stdout or "").splitlines())
def _pane_command(run: Runner, pane: str) -> str:
    result = run(
        ["tmux", "display-message", "-p", "-t", pane, "#{pane_current_command}"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return (result.stdout or "").strip() if result.returncode == 0 else ""
def _pane_session(run: Runner, pane: str) -> str:
    result = run(
        ["tmux", "display-message", "-p", "-t", pane, "#{session_name}"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return (result.stdout or "").strip() if result.returncode == 0 else ""
def _session_gone(run: Runner, session_name: str) -> bool:
    result = run(
        ["tmux", "has-session", "-t", session_name],
        check=False,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        return False
    stderr = result.stderr or ""
    return "can't find session" in stderr.casefold()
def _shell_cleanup_is_authorized(
    pane_command: str,
    session_name: str,
    session_prefix: str | None,
) -> bool:
    if session_prefix is None:
        return False
    return bool(pane_command in SHELL_PANE_COMMANDS and session_name and session_name.startswith(session_prefix))
def _forced_kill_cleanup_is_authorized(session_name: str, session_prefix: str | None) -> bool:
    if session_prefix is None:
        return True
    return bool(session_name and session_name.startswith(session_prefix))
def _capture(run: Runner, pane: str) -> str:
    result = run(
        ["tmux", "capture-pane", "-t", pane, "-p", "-S", "-40"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout or ""
def _clear_queued_exit(run: Runner, pane: str) -> bool:
    capture = _capture(run, pane)
    if "/exit" not in capture:
        return False
    _send_keys(run, pane, "Escape", "C-u")
    return True
def _looks_memory_prompt(capture: str) -> bool:
    return any(marker in capture for marker in MEMORY_PROMPT_MARKERS)
def _kill_pane_cleanup(run: Runner, pane: str) -> bool:
    if not _pane_exists(run, pane):
        return False
    result = run(["tmux", "kill-pane", "-t", pane], check=False)
    return result.returncode == 0
def _kill_shell_cleanup_target(run: Runner, pane: str, session_name: str) -> bool:
    return _kill_pane_cleanup(run, pane)
def _send_keys(run: Runner, pane: str, *keys: str) -> None:
    run(["tmux", "send-keys", "-t", pane, *keys], check=False)
def _submit_key_for_attempt(submit_key: str, attempt: int) -> str:
    if attempt % 2 == 1:
        return submit_key
    if submit_key == "C-m":
        return "C-j"
    if submit_key == "C-j":
        return "C-m"
    return "C-m"
def main(argv: list[str] | None = None) -> int:
    if __package__ in {None, ""}:
        from agent_orchestra_minimal.self_exit_cli import main as cli_main
    else:
        from .self_exit_cli import main as cli_main
    return cli_main(argv)
if __name__ == "__main__":
    raise SystemExit(main())
