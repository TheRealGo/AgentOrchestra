from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RUN_LOCAL_EVIDENCE_PREFIXES = (
    ".tmp/self-improvement-e2e/",
    ".tmp/self-improvement-e2e",
)
DEFAULT_SCANNED_DIRS = ("tests", "tests_claude", ".codex/agent_orchestra_minimal")


@dataclass(frozen=True)
class RunLocalReference:
    path: Path
    line_number: int
    text: str


def find_run_local_evidence_references(
    root: str | Path,
    *,
    scanned_dirs: tuple[str, ...] = DEFAULT_SCANNED_DIRS,
) -> list[RunLocalReference]:
    root_path = Path(root)
    references: list[RunLocalReference] = []
    for relative_dir in scanned_dirs:
        directory = root_path / relative_dir
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.py")):
            references.extend(_references_in_file(root_path, path))
    return references


def assert_no_run_local_evidence_references(root: str | Path) -> None:
    references = find_run_local_evidence_references(root)
    if references:
        formatted = ", ".join(f"{ref.path}:{ref.line_number}" for ref in references)
        raise ValueError(f"tracked runtime/tests reference run-local evidence paths: {formatted}")


def _references_in_file(root: Path, path: Path) -> list[RunLocalReference]:
    references: list[RunLocalReference] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return references
    for index, line in enumerate(text.splitlines(), start=1):
        if _line_reads_run_local_evidence(line):
            references.append(RunLocalReference(path.relative_to(root), index, line.strip()))
    return references


def _line_reads_run_local_evidence(line: str) -> bool:
    if not any(prefix in line for prefix in RUN_LOCAL_EVIDENCE_PREFIXES):
        return False
    return any(token in line for token in ("read_text(", "read_bytes(", "open("))
