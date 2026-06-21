from __future__ import annotations

from collections import Counter


def has_new_marker_line(capture: str, baseline_capture: str, markers: tuple[str, ...]) -> bool:
    baseline_counts = Counter(baseline_capture.splitlines())
    seen_counts: Counter[str] = Counter()
    for line in capture.splitlines():
        seen_counts[line] += 1
        if seen_counts[line] <= baseline_counts[line]:
            continue
        if line.strip().startswith(markers):
            return True
    return False
