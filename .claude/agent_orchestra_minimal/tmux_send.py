from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from agent_orchestra_minimal.tmux_delivery import DEFAULT_SUBMIT_KEY, DeliveryResult, Runner, send_buffered_text
    from agent_orchestra_minimal.tmux_peer_mailbox import enqueue_message, queued_messages, read_message, remove_message
else:
    from .tmux_delivery import DEFAULT_SUBMIT_KEY, DeliveryResult, Runner, send_buffered_text
    from .tmux_peer_mailbox import enqueue_message, queued_messages, read_message, remove_message


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
    parser.add_argument("--result-json")
    parser.add_argument("--queue-if-input-not-ready", action="store_true")
    parser.add_argument("--mailbox-dir")
    parser.add_argument("--sender", default="")
    parser.add_argument("--topic", default="")
    parser.add_argument("--drain-mailbox", action="store_true")
    args = parser.parse_args(argv)

    if args.drain_mailbox:
        result = _drain_mailbox(
            args.pane,
            submit_key=args.submit_key,
            mailbox_dir=args.mailbox_dir,
            max_retries=args.max_retries,
            poll_interval_seconds=args.poll_interval_seconds,
            polls_per_attempt=_effective_cli_polls_per_attempt(args.polls_per_attempt),
        )
        if args.result_json:
            _write_drain_result_json(Path(args.result_json), pane=args.pane, result=result)
        print(f"mailbox drain delivered {result['delivered']} of {result['queued']} queued message(s)")
        return 0 if result["failed"] == 0 else 1

    auto_drain_result: dict[str, object] | None = None
    if queued_messages(pane=args.pane, mailbox_dir=args.mailbox_dir):
        result = _drain_mailbox(
            args.pane,
            submit_key=args.submit_key,
            mailbox_dir=args.mailbox_dir,
            max_retries=args.max_retries,
            poll_interval_seconds=args.poll_interval_seconds,
            polls_per_attempt=_effective_cli_polls_per_attempt(args.polls_per_attempt),
        )
        if int(result["failed"]):
            if args.result_json:
                _write_drain_result_json(Path(args.result_json), pane=args.pane, result=result)
            print(f"mailbox drain failed before sending new message to {args.pane}")
            return 1
        auto_drain_result = result

    result = send_text(
        args.pane,
        args.text,
        submit_key=args.submit_key,
        max_retries=args.max_retries,
        poll_interval_seconds=args.poll_interval_seconds,
        polls_per_attempt=_effective_cli_polls_per_attempt(args.polls_per_attempt),
        require_fresh_capture=True,
    )
    queued_path: Path | None = None
    if args.queue_if_input_not_ready and not result.accepted:
        queued_path = enqueue_message(
            pane=args.pane,
            text=args.text,
            mailbox_dir=args.mailbox_dir,
            sender=args.sender,
            topic=args.topic,
        )
    if args.result_json:
        _write_result_json(Path(args.result_json), pane=args.pane, result=result, queued_path=queued_path, auto_drain_result=auto_drain_result)
    if result.accepted:
        print(f"accepted after {result.attempts} submit attempt(s)")
        return 0
    if queued_path is not None:
        print(f"target input was not ready; queued message for later drain: {queued_path}")
        return 0
    print("message was not accepted by target Claude Code TUI after retries")
    if result.capture_tail:
        print(result.capture_tail)
    return 1


def _effective_cli_polls_per_attempt(value: int) -> int:
    return max(value, MIN_CLI_POLLS_PER_ATTEMPT)


def _write_result_json(
    path: Path,
    *,
    pane: str,
    result: DeliveryResult,
    queued_path: Path | None = None,
    auto_drain_result: dict[str, object] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    queued = queued_path is not None
    path.write_text(
        json.dumps(
            {
                "pane": pane,
                "accepted": result.accepted,
                "attempts": result.attempts,
                "queued": queued,
                "queue_path": str(queued_path) if queued_path else "",
                "auto_drain": auto_drain_result or {},
                "ledger_candidate": "queued-consultation" if queued else "delivery-defect" if not result.accepted else "",
                "zero_issue_blocker": not result.accepted and not queued,
                "required_disposition": (
                    "drain queued consultation after the target pane becomes input-ready and record accepted drain evidence"
                    if queued
                    else "block completion until delivery succeeds or is dispositioned"
                    if not result.accepted
                    else ""
                ),
                "capture_tail": result.capture_tail,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _drain_mailbox(
    pane: str,
    *,
    submit_key: str,
    mailbox_dir: str | None,
    max_retries: int,
    poll_interval_seconds: float,
    polls_per_attempt: int,
    runner: Runner | None = None,
) -> dict[str, object]:
    paths = queued_messages(pane=pane, mailbox_dir=mailbox_dir)
    delivered: list[str] = []
    failed: list[dict[str, object]] = []
    for path in paths:
        message = read_message(path)
        result = send_text(
            pane,
            message["text"],
            submit_key=submit_key,
            max_retries=max_retries,
            poll_interval_seconds=poll_interval_seconds,
            polls_per_attempt=polls_per_attempt,
            require_fresh_capture=True,
            runner=runner,
        )
        if result.accepted:
            remove_message(path)
            delivered.append(str(path))
            continue
        failed.append({"path": str(path), "attempts": result.attempts, "capture_tail": result.capture_tail})
        break
    return {
        "queued": len(paths),
        "delivered": len(delivered),
        "failed": len(failed),
        "delivered_paths": delivered,
        "failed_messages": failed,
    }


def _write_drain_result_json(path: Path, *, pane: str, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    failed = int(result["failed"])
    path.write_text(
        json.dumps(
            {
                "pane": pane,
                "mailbox_drain": True,
                **result,
                "accepted": failed == 0,
                "ledger_candidate": "" if failed == 0 else "delivery-defect",
                "zero_issue_blocker": failed != 0,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
