from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from agent_orchestra_minimal import self_exit as self_exit_runtime
    from agent_orchestra_minimal.self_exit import SelfExitResult
else:
    from . import self_exit as self_exit_runtime
    from .self_exit import SelfExitResult


SELF_E2E_STATUS_DIR = Path(".tmp") / "self-improvement-e2e"


def launch_detached(
    *,
    pane: str,
    submit_key: str,
    result_path: Path | None,
    attempts: int,
    delay_seconds: float,
    allow_shell_cleanup_session_prefix: str | None,
    cleanup_auxiliary_shells: bool,
) -> int:
    child = os.fork()
    if child != 0:
        print(f"self-exit helper launched for {pane}; evidence={result_path or '<none>'}")
        return 0
    os.setsid()
    result = self_exit_runtime.run_self_exit(
        pane,
        submit_key=submit_key,
        attempts=attempts,
        delay_seconds=delay_seconds,
        allow_shell_cleanup_session_prefix=allow_shell_cleanup_session_prefix,
        cleanup_auxiliary_shells=cleanup_auxiliary_shells,
    )
    if result_path:
        _write_result(result_path, result)
    os._exit(0 if result.closed else 1)


def _write_result(path: Path, result: SelfExitResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _is_self_e2e_main_result_path(path: Path) -> bool:
    parts = path.parts
    if len(parts) < 3:
        return False
    return (
        path.name.startswith("main-self-exit")
        and path.suffix == ".json"
        and tuple(parts[-3:-1]) == tuple(SELF_E2E_STATUS_DIR.parts)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-orchestra-self-exit")
    parser.add_argument("--pane")
    parser.add_argument("--submit-key", default=os.environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", "C-m"))
    parser.add_argument("--result-path")
    parser.add_argument("--attempts", type=int, default=4)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument(
        "--allow-shell-cleanup-session-prefix",
        default=None,
        help=(
            "allow killing a non-Codex shell pane only when its tmux session "
            "name starts with this prefix, for dedicated SelfE2E cleanup"
        ),
    )
    parser.add_argument("--cleanup-auxiliary-shells", action="store_true")
    parser.add_argument("--foreground", action="store_true")
    args = parser.parse_args(argv)
    pane = args.pane or self_exit_runtime.resolve_pane()
    result_path = Path(args.result_path) if args.result_path else None
    if result_path is not None and _is_self_e2e_main_result_path(result_path):
        print(
            "agent-orchestra-self-exit: refusing direct SelfE2E main-self-exit "
            "evidence path; use agent_orchestra_minimal.self_e2e_finalizer so "
            "active-main-session, self-exit JSON, status readback, and "
            "dedicated-session-gone evidence are finalized atomically",
            file=sys.stderr,
        )
        return 2
    if args.foreground:
        result = self_exit_runtime.run_self_exit(
            pane,
            submit_key=args.submit_key,
            attempts=args.attempts,
            delay_seconds=args.delay_seconds,
            allow_shell_cleanup_session_prefix=args.allow_shell_cleanup_session_prefix,
            cleanup_auxiliary_shells=args.cleanup_auxiliary_shells,
        )
        if result_path:
            _write_result(result_path, result)
        print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
        return 0 if result.closed else 1
    return launch_detached(
        pane=pane,
        submit_key=args.submit_key,
        result_path=result_path,
        attempts=args.attempts,
        delay_seconds=args.delay_seconds,
        allow_shell_cleanup_session_prefix=args.allow_shell_cleanup_session_prefix,
        cleanup_auxiliary_shells=args.cleanup_auxiliary_shells,
    )


if __name__ == "__main__":
    raise SystemExit(main())
