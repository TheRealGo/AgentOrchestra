from __future__ import annotations

import re


MESSAGE_PROBE_CHARS = 120
MIN_MESSAGE_PROBE_CHARS = 56
MIN_TAIL_MESSAGE_PROBE_CHARS = 24
MAX_WRAPPED_PROBE_LINES = 24
START_MARKERS = ("• ", "Working", "Pursuing goal", "Explored", "Ran ", "Edited ")
LONG_START_MARKERS = ("Waiting for", "Finished waiting")
ACTIVE_STATUS_MARKERS = (
    "background terminal running",
    "background terminals running",
)
QUEUE_MARKERS = (
    "tab to queue message",
    "Messages to be submitted after next tool call",
)
BLOCKING_INPUT_MARKERS = (
    "Press enter to confirm",
    "esc to go back",
)
RECOVERABLE_CHOICE_MENU_MARKERS = (
    "esc to go back",
    "Switch to gpt-",
    "Keep current model",
    "Press enter to confirm or esc",
)
RECOVERABLE_STARTUP_MARKERS = (
    "Update available!",
    "MCP client failed",
    "MCP server failed",
    "failed to start MCP",
    "failed to initialize MCP",
    "startup warning",
    "less than 10% of your weekly limit left",
    "You've hit your usage limit",
    "Goal hit usage limits",
)
USAGE_LIMIT_MARKERS = (
    "You've hit your usage limit",
    "Goal hit usage limits",
)
DEFAULT_COMPOSER_PROMPTS = (
    "Find and fix a bug in @filename",
    "Write tests for @filename",
    "Improve documentation in @filename",
    "Explain this codebase",
    "Implement {feature}",
    "Summarize recent commits",
    "Run /review on my current changes",
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


def line_has_default_composer_prompt(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped.startswith(("›", ">")):
        return False
    message = stripped[1:].strip()
    return any(message.startswith(prompt) for prompt in DEFAULT_COMPOSER_PROMPTS)


def line_has_clearable_composer_prompt(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped.startswith(("›", ">")):
        return False
    if line_has_agent_message_prompt(line):
        return False
    message = stripped[1:].strip()
    return bool(message)


def looks_started(capture: str) -> bool:
    return any(
        line_has_start_marker(line, START_MARKERS + LONG_START_MARKERS)
        for line in capture.splitlines()
    )


def line_has_start_marker(line: str, markers: tuple[str, ...]) -> bool:
    if line[:1].isspace():
        return False
    if line.startswith(("• Starting MCP servers", "• No previous message to edit.")):
        return False
    return any(line.startswith(marker) for marker in markers)


def has_active_marker(lines: list[str]) -> bool:
    active_markers = ("• Working", "Working", "Pursuing goal")
    done_markers = ("Done.", "Done", "FAILED", "Failed", "Cancelled", "─ Worked for")
    active_index = max(
        (i for i, line in enumerate(lines) if line_has_start_marker(line, active_markers)),
        default=-1,
    )
    if active_index <= max(
        (i for i, line in enumerate(lines) if line_has_start_marker(line, done_markers)),
        default=-1,
    ):
        return any(any(marker in line for marker in ACTIVE_STATUS_MARKERS) for line in lines)
    return True


def looks_interrupted_or_paused(capture: str) -> bool:
    return any(
        line.lstrip().startswith("■ Conversation interrupted")
        or line.lstrip().startswith("■ Something went wrong")
        or "tell the model what to do differently" in line
        or (
            line.lstrip().startswith("gpt-")
            and ("Goal paused" in line or "Goal blocked" in line)
        )
        for line in capture.splitlines()
    )


def looks_usage_limited(capture: str) -> bool:
    return any(marker in capture for marker in USAGE_LIMIT_MARKERS)


def same_ready_prompt_started_work(
    lines: list[str],
    prompt_index: int,
    tail: str,
    *,
    baseline_capture: str,
    baseline_prompt_index: int,
) -> bool:
    if baseline_prompt_index == -1 or prompt_index != baseline_prompt_index:
        return False
    baseline_lines = baseline_capture.splitlines()
    if prompt_index >= len(baseline_lines):
        return False
    prompt_line = lines[prompt_index]
    if prompt_line != baseline_lines[prompt_index]:
        return False
    if line_has_agent_message_prompt(prompt_line):
        return False
    return looks_started(tail)


def agent_prompt_started_work_without_probe(
    lines: list[str],
    prompt_index: int,
    text: str,
    tail: str,
    *,
    baseline_capture: str,
) -> bool:
    if not line_has_agent_message_prompt(lines[prompt_index]):
        return False
    if not looks_started(tail) or looks_queued(tail):
        return False
    prompt_text = normalized_wrapped_line_window(lines, prompt_index).lstrip("›> ")
    normalized_text = " ".join(text.strip().split())
    return (
        (
            prompt_text == normalized_text
            or (
                len(prompt_text) >= MIN_MESSAGE_PROBE_CHARS
                and normalized_text.startswith(prompt_text)
            )
        )
        and "\n".join(lines) != baseline_capture
    )


def looks_queued(capture: str) -> bool:
    return any(line_has_queue_marker(line) for line in capture.splitlines())


def looks_queued_before_started(capture: str) -> bool:
    for line in capture.splitlines():
        if line_has_queue_marker(line):
            return True
        if line_has_start_marker(line, START_MARKERS + LONG_START_MARKERS):
            return False
    return False


def line_has_queue_marker(line: str) -> bool:
    return any(marker in line for marker in QUEUE_MARKERS)


def looks_blocked_by_input_choice(capture: str) -> bool:
    return any(marker in capture for marker in BLOCKING_INPUT_MARKERS)


def looks_recoverable_choice_menu(capture: str) -> bool:
    return any(marker in capture for marker in RECOVERABLE_CHOICE_MENU_MARKERS)


def looks_recoverable_startup_notice(capture: str) -> bool:
    lowered = capture.casefold()
    return any(marker.casefold() in lowered for marker in RECOVERABLE_STARTUP_MARKERS)


def looks_startup_in_progress(capture: str) -> bool:
    return "starting mcp servers" in capture.casefold()


def message_probes(text: str) -> tuple[str, ...]:
    normalized = " ".join(text.strip().split())
    first_line = " ".join(text.strip().splitlines()[0].split()) if text.strip() else ""
    nonempty_lines = [" ".join(line.split()) for line in text.strip().splitlines() if line.strip()]
    last_long_line = next(
        (line for line in reversed(nonempty_lines) if len(line) >= MIN_MESSAGE_PROBE_CHARS),
        "",
    )
    tail = normalized[-MESSAGE_PROBE_CHARS:] if len(normalized) >= MIN_MESSAGE_PROBE_CHARS else ""
    probes = []
    for source in (normalized, first_line, last_long_line, tail):
        for length in (MESSAGE_PROBE_CHARS, 80, MIN_MESSAGE_PROBE_CHARS):
            candidate = source[:length]
            if candidate and (len(source) <= length or len(candidate) >= MIN_MESSAGE_PROBE_CHARS):
                if candidate not in probes:
                    probes.append(candidate)
    for source in reversed(nonempty_lines):
        if len(source) >= MIN_TAIL_MESSAGE_PROBE_CHARS:
            candidate = source[:MIN_MESSAGE_PROBE_CHARS]
            if candidate not in probes:
                probes.append(candidate)
            break
    if len(normalized) >= MIN_TAIL_MESSAGE_PROBE_CHARS:
        candidate = normalized[-MIN_MESSAGE_PROBE_CHARS:]
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
