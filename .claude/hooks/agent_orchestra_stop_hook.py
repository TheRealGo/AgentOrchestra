#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


# This hook is installed at ``$CLAUDE_CONFIG_DIR/hooks/`` and the runtime package
# is copied next to it at ``$CLAUDE_CONFIG_DIR/agent_orchestra_minimal/``.
RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from agent_orchestra_minimal.tmux_wake import run_stop_hook


def main() -> int:
    # Claude Code delivers Stop Hook context as JSON on stdin (session_id,
    # transcript_path, cwd, hook_event_name, stop_hook_active). The runtime
    # re-kick decision is driven by the launch-provided environment and the
    # shared task/state files, so the payload is read to drain the pipe and is
    # otherwise advisory.
    _read_stop_payload()
    try:
        decision = run_stop_hook(os.environ)
    except Exception as exc:
        print(f"agent-orchestra Stop Hook skipped: {exc}", file=sys.stderr)
    else:
        if decision and "wake_delivery" in decision.reason:
            print(f"agent-orchestra Stop Hook wake issue: {decision.reason}", file=sys.stderr)
    # Exit 0: re-kick is delivered as an external tmux wake, not as a native
    # blocking decision, so the hook never blocks Claude Code from stopping.
    return 0


def _read_stop_payload() -> dict[str, object]:
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
