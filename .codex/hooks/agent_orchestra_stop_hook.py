#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


CODEX_DIR = Path(__file__).resolve().parents[1]
if str(CODEX_DIR) not in sys.path:
    sys.path.insert(0, str(CODEX_DIR))

from agent_orchestra_minimal.tmux_wake import run_stop_hook


def main() -> int:
    try:
        run_stop_hook(os.environ)
    except Exception as exc:
        print(f"agent-orchestra Stop Hook skipped: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
