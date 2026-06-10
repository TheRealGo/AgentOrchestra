from __future__ import annotations

import argparse
import sys
from pathlib import Path


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from agent_orchestra_minimal.tmux_delivery import DEFAULT_SUBMIT_KEY, DeliveryResult, Runner, send_buffered_text
else:
    from .tmux_delivery import DEFAULT_SUBMIT_KEY, DeliveryResult, Runner, send_buffered_text


BUFFER_PREFIX = "agent-orchestra-msg"
MIN_CLI_POLLS_PER_ATTEMPT = 60


def send_text(
    pane_target: str,
    text: str,
    *,
    submit_key: str = DEFAULT_SUBMIT_KEY,
    runner: Runner | None = None,
    max_retries: int = 2,
    poll_interval_seconds: float = 0.2,
    polls_per_attempt: int = 1,
    require_fresh_capture: bool = True,
) -> DeliveryResult:
    return send_buffered_text(
        pane_target,
        text,
        buffer_prefix=BUFFER_PREFIX,
        submit_key=submit_key,
        runner=runner,
        max_retries=max_retries,
        poll_interval_seconds=poll_interval_seconds,
        polls_per_attempt=polls_per_attempt,
        require_fresh_capture=require_fresh_capture,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-orchestra-tmux-send")
    parser.add_argument("--pane", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--submit-key", default=DEFAULT_SUBMIT_KEY)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--poll-interval-seconds", type=float, default=0.5)
    parser.add_argument("--polls-per-attempt", type=int, default=60)
    args = parser.parse_args(argv)

    result = send_text(
        args.pane,
        args.text,
        submit_key=args.submit_key,
        max_retries=args.max_retries,
        poll_interval_seconds=args.poll_interval_seconds,
        polls_per_attempt=_effective_cli_polls_per_attempt(args.polls_per_attempt),
        require_fresh_capture=True,
    )
    if result.accepted:
        print(f"accepted after {result.attempts} submit attempt(s)")
        return 0
    print("message was not accepted by target Claude Code TUI after retries")
    if result.capture_tail:
        print(result.capture_tail)
    return 1


def _effective_cli_polls_per_attempt(value: int) -> int:
    return max(value, MIN_CLI_POLLS_PER_ATTEMPT)


if __name__ == "__main__":
    raise SystemExit(main())
