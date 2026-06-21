from __future__ import annotations

import subprocess
from collections.abc import Callable


Runner = Callable[..., subprocess.CompletedProcess[str]]
SHELL_PANE_COMMANDS = frozenset({"bash", "zsh", "sh", "fish"})


def cleanup_auxiliary_shell_panes(
    run: Runner,
    *,
    session_name: str,
    session_prefix: str | None,
    exclude_pane: str,
) -> tuple[str, ...]:
    if not session_prefix or not session_name.startswith(session_prefix):
        return ()
    result = run(
        ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}\t#{pane_current_command}"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return ()
    killed: list[str] = []
    for line in (result.stdout or "").splitlines():
        pane, separator, command = line.partition("\t")
        if not separator or pane == exclude_pane or command not in SHELL_PANE_COMMANDS:
            continue
        kill = run(["tmux", "kill-pane", "-t", pane], check=False)
        if kill.returncode == 0:
            killed.append(pane)
    return tuple(killed)
