from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

from .tmux_targets import required_tmux_pane


CODEX_COMMANDS = frozenset({"codex", "node"})
SHELL_COMMANDS = frozenset({"bash", "zsh", "sh", "fish"})


@dataclass(frozen=True)
class PaneIdentity:
    session_name: str
    pane: str
    command: str
    cwd: str


@dataclass(frozen=True)
class PaneVerification:
    valid: bool
    pane: str
    reasons: tuple[str, ...]
    identity: PaneIdentity | None


def verify_pane_identity(
    *,
    expected_pane: str,
    expected_session: str,
    expected_cwd: str,
    display_line: str,
    capture: str,
) -> PaneVerification:
    pane = required_tmux_pane(expected_pane)
    reasons: list[str] = []
    identity = parse_display_line(display_line)
    if identity is None:
        return PaneVerification(False, pane, ("display-line-unparseable",), None)
    if identity.pane != pane:
        reasons.append("pane-id-mismatch")
    if identity.session_name != expected_session:
        reasons.append("session-mismatch")
    if identity.command in SHELL_COMMANDS:
        reasons.append("shell-process")
    elif identity.command not in CODEX_COMMANDS:
        reasons.append("non-codex-process")
    if Path(identity.cwd).expanduser() != Path(expected_cwd).expanduser():
        reasons.append("cwd-mismatch")
    if not capture_shows_codex_tui(capture):
        reasons.append("tui-capture-missing")
    return PaneVerification(not reasons, pane, tuple(reasons), identity)


def parse_display_line(line: str) -> PaneIdentity | None:
    parts = line.rstrip("\n").split(" ", 3)
    if len(parts) != 4:
        return None
    session_window, pane, command, cwd = parts
    session_name = session_window.split(":", 1)[0]
    if not session_name or not pane or not command or not cwd:
        return None
    return PaneIdentity(session_name=session_name, pane=pane, command=command, cwd=cwd)


def capture_shows_codex_tui(capture: str) -> bool:
    text = capture.strip()
    if not text:
        return False
    markers = ("OpenAI Codex", "›", ">_", "gpt-")
    return any(marker in text for marker in markers)


def verify_live_pane(
    *,
    expected_pane: str,
    expected_session: str,
    expected_cwd: str,
    capture_lines: int,
) -> PaneVerification:
    pane = required_tmux_pane(expected_pane)
    display = subprocess.run(
        [
            "tmux",
            "display-message",
            "-p",
            "-t",
            pane,
            "#{session_name}:#{window_index}.#{pane_index} #{pane_id} #{pane_current_command} #{pane_current_path}",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout
    capture = subprocess.run(
        ["tmux", "capture-pane", "-t", pane, "-p", "-S", f"-{capture_lines}"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout
    return verify_pane_identity(
        expected_pane=pane,
        expected_session=expected_session,
        expected_cwd=expected_cwd,
        display_line=display,
        capture=capture,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="verify a ProfessionalAgent pane before task delivery")
    parser.add_argument("--pane", required=True)
    parser.add_argument("--expected-session", required=True)
    parser.add_argument("--expected-cwd", required=True)
    parser.add_argument("--capture-lines", type=int, default=120)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = verify_live_pane(
        expected_pane=args.pane,
        expected_session=args.expected_session,
        expected_cwd=args.expected_cwd,
        capture_lines=args.capture_lines,
    )
    if args.json:
        print(json.dumps(asdict(result), sort_keys=True))
    elif result.valid:
        print(f"{result.pane}: verified")
    else:
        print(f"{result.pane}: invalid: {','.join(result.reasons)}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
