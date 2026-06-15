from __future__ import annotations

import contextlib
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None  # type: ignore[assignment]


@contextlib.contextmanager
def manifest_lock(path: Path):
    lock_path = path.with_name(f"{path.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a", encoding="utf-8") as lock_file:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
