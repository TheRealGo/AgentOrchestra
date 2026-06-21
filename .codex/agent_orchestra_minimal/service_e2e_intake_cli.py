from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .service_e2e_intake import (
    append_self_improvement_intake_to_task_file,
    render_self_improvement_intake_from_brief,
)


def service_e2e_intake_command(args: argparse.Namespace) -> int:
    try:
        brief = _service_e2e_brief(args)
        rendered = (
            append_self_improvement_intake_to_task_file(
                task_file_path=args.task_file,
                defect_brief=brief,
            )
            if args.task_file
            else render_self_improvement_intake_from_brief(brief)
        )
    except (OSError, ValueError) as exc:
        print(f"agent-orchestra service-e2e-intake: failed: {exc}", file=sys.stderr)
        return 1
    for section in ("Backlog", "Acceptance", "Gates", "Candidates"):
        print(f"[{section}]")
        for line in rendered[section]:
            print(line)
    if args.task_file:
        print(f"agent-orchestra service-e2e-intake: appended to {args.task_file}", file=sys.stderr)
    return 0


def _service_e2e_brief(args: argparse.Namespace) -> str:
    if args.brief and args.brief_file:
        raise ValueError("use only one of --brief or --brief-file")
    if args.brief_file:
        return Path(args.brief_file).expanduser().read_text(encoding="utf-8")
    if args.brief:
        return args.brief
    return sys.stdin.read()
