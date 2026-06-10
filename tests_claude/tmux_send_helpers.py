from __future__ import annotations

import subprocess


class FakeTmuxSend:
    def __init__(self, captures: list[str], *, baseline_capture: str | None = "") -> None:
        self.captures = captures
        self.baseline_capture = baseline_capture
        self.calls: list[tuple[list[str], str | None]] = []
        self.paste_seen = False

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        payload = kwargs.get("input") if isinstance(kwargs.get("input"), str) else None
        self.calls.append((args, payload))
        stdout = ""
        if args[:2] == ["tmux", "paste-buffer"]:
            self.paste_seen = True
        if args[:2] == ["tmux", "capture-pane"]:
            if not self.paste_seen and self.baseline_capture is not None:
                stdout = self.baseline_capture
            else:
                stdout = self.captures.pop(0) if self.captures else ""
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


def tmux_buffer_name(fake: FakeTmuxSend) -> str:
    if not fake.calls:
        raise AssertionError("expected tmux load-buffer call")
    args = fake.calls[0][0]
    if args[:3] != ["tmux", "load-buffer", "-b"]:
        raise AssertionError(f"unexpected first tmux call: {args!r}")
    if not args[3].startswith("agent-orchestra-msg-"):
        raise AssertionError(f"unexpected buffer name: {args[3]!r}")
    return args[3]
