from __future__ import annotations

import os
import re
from collections.abc import Mapping


SAFE_PARENT_ENV_KEYS = frozenset(
    {
        "COLORTERM",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "NIX_PROFILES",
        "NIX_SSL_CERT_FILE",
        "PATH",
        "SHELL",
        "SSH_AUTH_SOCK",
        "TERM",
        "TERM_PROGRAM",
        "TERM_PROGRAM_VERSION",
        "TMPDIR",
        "USER",
        "XDG_DATA_DIRS",
    }
)
SAFE_PARENT_ENV_PREFIXES = ("GHOSTTY_",)
SECRET_ENV_NAME = re.compile(r"(TOKEN|SECRET|PASSWORD|PASSWD|API[_-]?KEY|ACCESS[_-]?KEY|PRIVATE[_-]?KEY|CREDENTIAL)", re.I)


def clean_codex_env(
    agent_env: Mapping[str, str],
    *,
    parent_env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in (parent_env or os.environ).items():
        if _safe_parent_key(key):
            result[key] = value
    result.update(agent_env)
    return {key: value for key, value in result.items() if not SECRET_ENV_NAME.search(key)}


def _safe_parent_key(key: str) -> bool:
    return key in SAFE_PARENT_ENV_KEYS or any(key.startswith(prefix) for prefix in SAFE_PARENT_ENV_PREFIXES)
