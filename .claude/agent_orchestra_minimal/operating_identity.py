from __future__ import annotations

from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent / "agent_templates"


def read_agent_template(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text(encoding="utf-8").strip()


AGENT_ORCHESTRA_OPERATING_IDENTITY = read_agent_template("common.CLAUDE.md")


def role_contract(agent_kind: str) -> str:
    if agent_kind == "MainAgent":
        return read_agent_template("main.CLAUDE.md")
    return read_agent_template("professional.CLAUDE.md")
