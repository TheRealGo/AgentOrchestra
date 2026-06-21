from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from agent_orchestra_minimal.self_e2e_status import SelfE2EStatusResult, finalize_status_after_task_readback
    from agent_orchestra_minimal.self_exit import SelfExitResult, run_self_exit
    from agent_orchestra_minimal.self_e2e_task_mirror import mirror_self_e2e_blockers_to_task_file
    from agent_orchestra_minimal.tmux_delivery import normalize_submit_key
    from agent_orchestra_minimal.tmux_targets import required_tmux_pane
else:
    from .self_e2e_status import SelfE2EStatusResult, finalize_status_after_task_readback
    from .self_exit import SelfExitResult, run_self_exit
    from .self_e2e_task_mirror import mirror_self_e2e_blockers_to_task_file
    from .tmux_delivery import normalize_submit_key
    from .tmux_targets import required_tmux_pane


Runner = object
SELF_E2E_SESSION_PREFIX = "AgentOrchestra-self-e2e-"


@dataclass(frozen=True)
class SelfE2EFinalizeAfterExitResult:
    self_exit: SelfExitResult
    status: SelfE2EStatusResult
    result_path: str
    active_main_session_path: str


def run_finalize_after_self_exit(
    *,
    pane: str,
    task_file_path: str | Path,
    status_path: str | Path,
    result_path: str | Path,
    submit_key: str,
    attempts: int = 4,
    delay_seconds: float = 2.0,
    allow_shell_cleanup_session_prefix: str = SELF_E2E_SESSION_PREFIX,
    cleanup_auxiliary_shells: bool = True,
    runner: object = subprocess.run,
    sleeper: object = time.sleep,
) -> SelfE2EFinalizeAfterExitResult:
    pane = required_tmux_pane(pane)
    submit_key = normalize_submit_key(submit_key)
    status_file = Path(status_path)
    result_file = Path(result_path)
    status_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.parent.mkdir(parents=True, exist_ok=True)

    session_name = _tmux_session_name(pane, runner=runner)
    _validate_self_e2e_target(
        status_file.parent,
        pane=pane,
        session_name=session_name,
        allowed_session_prefix=allow_shell_cleanup_session_prefix,
    )
    active_main_session_path = _write_active_main_session(status_file.parent, pane=pane, session_name=session_name)

    self_exit = run_self_exit(
        pane,
        submit_key=submit_key,
        runner=runner,  # type: ignore[arg-type]
        sleeper=sleeper,  # type: ignore[arg-type]
        attempts=attempts,
        delay_seconds=delay_seconds,
        allow_shell_cleanup_session_prefix=allow_shell_cleanup_session_prefix,
        cleanup_auxiliary_shells=cleanup_auxiliary_shells,
    )
    result_file.write_text(
        json.dumps(asdict(self_exit), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    status = finalize_status_after_task_readback(
        status_path=status_file,
        task_file_path=task_file_path,
        active_main_pane=pane,
        active_main_session_name=session_name,
        self_exit_result_path=result_file,
    )
    mirror_self_e2e_blockers_to_task_file(
        task_file_path=task_file_path,
        status=status,
    )
    return SelfE2EFinalizeAfterExitResult(
        self_exit=self_exit,
        status=status,
        result_path=str(result_file),
        active_main_session_path=str(active_main_session_path),
    )


def launch_detached_finalize_after_self_exit(
    *,
    pane: str,
    task_file_path: str | Path,
    status_path: str | Path,
    result_path: str | Path,
    submit_key: str,
    attempts: int,
    delay_seconds: float,
    allow_shell_cleanup_session_prefix: str,
    cleanup_auxiliary_shells: bool,
) -> int:
    child = os.fork()
    if child != 0:
        print(f"self-e2e finalizer launched for {pane}; evidence={result_path}")
        return 0
    os.setsid()
    result = run_finalize_after_self_exit(
        pane=pane,
        task_file_path=task_file_path,
        status_path=status_path,
        result_path=result_path,
        submit_key=submit_key,
        attempts=attempts,
        delay_seconds=delay_seconds,
        allow_shell_cleanup_session_prefix=allow_shell_cleanup_session_prefix,
        cleanup_auxiliary_shells=cleanup_auxiliary_shells,
    )
    os._exit(0 if result.self_exit.closed and result.status.status == "done" else 1)


def _tmux_session_name(pane: str, *, runner: object = subprocess.run) -> str:
    try:
        result = runner(  # type: ignore[operator]
            ["tmux", "display-message", "-p", "-t", pane, "#{session_name}"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return ""
    return (result.stdout or "").strip() if result.returncode == 0 else ""


def _write_active_main_session(status_dir: Path, *, pane: str, session_name: str) -> Path:
    path = status_dir / "active-main-session.json"
    path.write_text(
        json.dumps(
            {
                "pane": pane,
                "session_name": session_name,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _validate_self_e2e_target(
    status_dir: Path,
    *,
    pane: str,
    session_name: str,
    allowed_session_prefix: str,
) -> None:
    if not allowed_session_prefix:
        raise ValueError("self-e2e finalizer requires a dedicated tmux session prefix")
    if not session_name.startswith(allowed_session_prefix):
        raise ValueError(
            "self-e2e finalizer target must be in the dedicated "
            f"{allowed_session_prefix!r} tmux session, got {session_name!r}"
        )
    binding_path = status_dir / "active-main-session.json"
    if not binding_path.is_file():
        return
    try:
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid active-main-session binding: {binding_path}") from exc
    expected_pane = binding.get("pane")
    expected_session = binding.get("session_name")
    if expected_pane != pane or expected_session != session_name:
        raise ValueError(
            "self-e2e finalizer target does not match active-main-session "
            f"binding: expected pane={expected_pane!r} session={expected_session!r}, "
            f"got pane={pane!r} session={session_name!r}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-orchestra-self-e2e-finalizer")
    parser.add_argument("--pane", required=True)
    parser.add_argument("--task-file", required=True)
    parser.add_argument("--status-path", required=True)
    parser.add_argument("--result-path", required=True)
    parser.add_argument("--submit-key", default=os.environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", "C-m"))
    parser.add_argument("--attempts", type=int, default=4)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument(
        "--allow-shell-cleanup-session-prefix",
        default=SELF_E2E_SESSION_PREFIX,
        help="allow cleanup only for the dedicated SelfE2E tmux session prefix",
    )
    parser.add_argument("--no-cleanup-auxiliary-shells", action="store_true")
    parser.add_argument(
        "--cleanup-auxiliary-shells",
        action="store_true",
        help="explicitly keep default same-session auxiliary shell cleanup enabled",
    )
    parser.add_argument("--foreground", action="store_true")
    args = parser.parse_args(argv)

    if args.foreground:
        result = run_finalize_after_self_exit(
            pane=args.pane,
            task_file_path=args.task_file,
            status_path=args.status_path,
            result_path=args.result_path,
            submit_key=args.submit_key,
            attempts=args.attempts,
            delay_seconds=args.delay_seconds,
            allow_shell_cleanup_session_prefix=args.allow_shell_cleanup_session_prefix,
            cleanup_auxiliary_shells=not args.no_cleanup_auxiliary_shells,
        )
        print(
            json.dumps(
                {
                    "self_exit": asdict(result.self_exit),
                    "status": asdict(result.status),
                    "result_path": result.result_path,
                    "active_main_session_path": result.active_main_session_path,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0 if result.self_exit.closed and result.status.status == "done" else 1

    return launch_detached_finalize_after_self_exit(
        pane=args.pane,
        task_file_path=args.task_file,
        status_path=args.status_path,
        result_path=args.result_path,
        submit_key=args.submit_key,
        attempts=args.attempts,
        delay_seconds=args.delay_seconds,
        allow_shell_cleanup_session_prefix=args.allow_shell_cleanup_session_prefix,
        cleanup_auxiliary_shells=not args.no_cleanup_auxiliary_shells,
    )


if __name__ == "__main__":
    raise SystemExit(main())
