from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.autonomy_policy import SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS  # noqa: E402
from agent_orchestra_minimal.task_file import DEFAULT_TASK_FILE  # noqa: E402


SERVICE_E2E_REPLAY_EVIDENCE = " ".join(
    f"service-e2e-approval-replay-{observation.defect_id}"
    for observation in SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS
)


SELF_E2E_FINALIZED_TASK_FILE = DEFAULT_TASK_FILE.replace(
    "[Acceptance]\n\n",
    (
        "[Acceptance]\n"
        "REQ-001: status=satisfied; source=SPEC.md; owner=main; "
        "verification=selfe2e-finalization; "
        "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
        "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
        "main-self-exit.json closed=true auxiliary_shell_panes same-session "
        "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
    ),
).replace(
    "[Gates]\n\n",
    (
        "[Gates]\n"
        "gate-selfe2e-depth: status=passed; kind=e2e; "
        "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
        "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
        "main-self-exit.json closed=true auxiliary_shell_panes same-session "
        "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
    ),
).replace(
    "[Candidates]\n\n",
    (
        "[Candidates]\n"
        "selfe2e-depth: disposition=integrated; "
        "summary=SelfE2E finalization depth evidence complete; "
        "evidence=service-e2e-intake worker-path service-approval-replay execution-path-proof ProfessionalAgent-review "
        "multi-viewpoint-search standard-verification final-candidate-sweep CAO-intervention-disposition copied-runtime "
        "main-self-exit.json closed=true auxiliary_shell_panes same-session "
        "dedicated-session-gone active-main-session pane session no-CAO-cleanup\n\n"
    ),
).replace(
    "[Done]\n",
    f"[Done]\nselfe2e-replay-evidence: evidence={SERVICE_E2E_REPLAY_EVIDENCE}\n",
)


def write_self_exit_result(
    status_file: Path,
    *,
    closed: bool = True,
    session_name: str = "AgentOrchestra-self-e2e-20260621-200315",
    auxiliary_shell_panes: list[str] | None = None,
    reason: str = "pane_closed",
    pane: str = "%439",
    write_active_main: bool = True,
    active_pane: str | None = None,
    active_session_name: str | None = None,
    session_gone: bool = True,
) -> Path:
    result_path = status_file.parent / "main-self-exit.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    if write_active_main:
        (status_file.parent / "active-main-session.json").write_text(
            json.dumps(
                {
                    "pane": active_pane if active_pane is not None else pane,
                    "session_name": active_session_name if active_session_name is not None else session_name,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    result_path.write_text(
        json.dumps(
            {
                "attempts": 1,
                "auxiliary_shell_panes": auxiliary_shell_panes if auxiliary_shell_panes is not None else ["%440", "%441"],
                "cleared_leftover": False,
                "closed": closed,
                "killed_pane": False,
                "pane": pane,
                "reason": reason,
                "session_name": session_name,
                "session_gone": session_gone,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return result_path
