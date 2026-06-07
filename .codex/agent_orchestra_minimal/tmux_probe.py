from __future__ import annotations

import re


MESSAGE_PROBE_CHARS = 120
MIN_MESSAGE_PROBE_CHARS = 56
MAX_WRAPPED_PROBE_LINES = 24
START_MARKERS = ("• ", "Working", "Pursuing goal", "Explored", "Ran ", "Edited ")
LONG_START_MARKERS = ("Waiting for", "Finished waiting")
QUEUE_MARKERS = (
    "tab to queue message",
    "Messages to be submitted after next tool call",
)
AGENT_MESSAGE_ROLES = ("MainAgent", "ProfessionalAgent")
AGENT_ID_PROMPT = re.compile(r"^(?:main|mainagent|pro-[A-Za-z0-9_.-]+)(?::|\s|$)")


def last_probe_index(lines: list[str], text: str) -> int:
    probes = message_probes(text)
    if not probes:
        return -1
    for index in range(len(lines) - 1, -1, -1):
        stripped = normalized_wrapped_line_window(lines, index)
        if any(probe_matches(probe, stripped) for probe in probes):
            return wrapped_line_window_end(lines, index)
    return -1


def normalized_wrapped_line_window(lines: list[str], start: int) -> str:
    window = [lines[start]]
    for line in lines[start + 1 : start + MAX_WRAPPED_PROBE_LINES]:
        if not line[:1].isspace() or line_has_queue_marker(line):
            break
        window.append(line)
    return " ".join(" ".join(line.strip().split()) for line in window)


def wrapped_line_window_end(lines: list[str], start: int) -> int:
    end = start
    for index, line in enumerate(lines[start + 1 : start + MAX_WRAPPED_PROBE_LINES], start + 1):
        if not line[:1].isspace() or line_has_queue_marker(line):
            break
        end = index
    return end


def last_prompt_marker_index(lines: list[str]) -> int:
    for index in range(len(lines) - 1, -1, -1):
        if line_has_prompt_marker(lines[index]):
            return index
    return -1


def line_has_prompt_marker(line: str) -> bool:
    return line.lstrip().startswith(("›", ">"))


def line_has_agent_message_prompt(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped.startswith(("›", ">")):
        return False
    message = stripped[1:].lstrip()
    return AGENT_ID_PROMPT.match(message) is not None or any(
        message == role
        or message.startswith(f"{role}:")
        or message.startswith(f"{role} ")
        for role in AGENT_MESSAGE_ROLES
    )


def looks_started(capture: str) -> bool:
    return any(
        line_has_start_marker(line, START_MARKERS + LONG_START_MARKERS)
        for line in capture.splitlines()
    )


def line_has_start_marker(line: str, markers: tuple[str, ...]) -> bool:
    if line[:1].isspace():
        return False
    return any(line.startswith(marker) for marker in markers)


def looks_queued(capture: str) -> bool:
    return any(line_has_queue_marker(line) for line in capture.splitlines())


def line_has_queue_marker(line: str) -> bool:
    return any(marker in line for marker in QUEUE_MARKERS)


def message_probes(text: str) -> tuple[str, ...]:
    normalized = " ".join(text.strip().split())
    first_line = " ".join(text.strip().splitlines()[0].split()) if text.strip() else ""
    probes = []
    for source in (normalized, first_line):
        for length in (MESSAGE_PROBE_CHARS, 80, MIN_MESSAGE_PROBE_CHARS):
            candidate = source[:length]
            if candidate and (len(source) <= length or len(candidate) >= MIN_MESSAGE_PROBE_CHARS):
                if candidate not in probes:
                    probes.append(candidate)
    return tuple(probes)


def probe_matches(probe: str, capture_window: str) -> bool:
    if probe in capture_window:
        return True
    if not has_non_ascii(probe):
        return False
    return without_whitespace(probe) in without_whitespace(capture_window)


def has_non_ascii(text: str) -> bool:
    return any(ord(character) > 127 for character in text)


def without_whitespace(text: str) -> str:
    return "".join(text.split())
