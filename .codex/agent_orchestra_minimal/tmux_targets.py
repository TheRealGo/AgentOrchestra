from __future__ import annotations

import re
from typing import Any


TMUX_PANE_TARGET = re.compile(r"^%[A-Za-z0-9_.:-]+$")


def optional_tmux_pane(value: Any) -> str | None:
    if value is None:
        return None
    pane = str(value).strip()
    if not pane:
        return None
    if not TMUX_PANE_TARGET.fullmatch(pane):
        raise ValueError("tmux pane target must be a deterministic %pane id")
    return pane


def required_tmux_pane(value: Any) -> str:
    pane = optional_tmux_pane(value)
    if pane is None:
        raise ValueError("pane_target is required")
    return pane
