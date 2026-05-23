---
name: agent-orchestra-task-file
description: Maintain the shared agent-orchestra task file so Hook-driven re-kick behavior follows deterministic progress/done and Backlog/InProgress/InReview/Done state.
---

# agent-orchestra Task File Skill

Use this Skill when updating the shared task file for an agent-orchestra run.
The task file is the deterministic source for whether MainAgent should be
re-kicked after stopping.

## Shape

```ini
[status]
progress

[Backlog]

[InProgress]

[InReview]

[Done]
```

`[status]` is either `progress` or `done`.

Open work is any item in `[Backlog]`, `[InProgress]`, or `[InReview]`.
`[Done]` does not count as open work.

## Update Rules

- Add newly discovered work under `[Backlog]`.
- Move active work from `[Backlog]` to `[InProgress]`.
- Move work awaiting MainAgent review to `[InReview]`.
- Move accepted work to `[Done]`.
- Set `[status]` to `progress` whenever open work exists or discovery is still
  active.
- Set `[status]` to `done` only after `[Backlog]`, `[InProgress]`, and
  `[InReview]` are empty.
- Finalize in this order: first move accepted or deferred items out of open
  sections, then verify `[Backlog]`, `[InProgress]`, and `[InReview]` are empty,
  and only then write `[status] done`.
- Never write `[status] done` while any real open item remains. `done` with
  open work is a Hook re-kick condition, not a normal intermediate state.
- Do not stop, mark a goal `blocked`, or leave the run awaiting Hook wake while
  `[Backlog]`, `[InProgress]`, or `[InReview]` contains work the AgentTeam can
  still advance.
- If work cannot be advanced because it requires user input or an external
  state change, remove it from open sections before stopping and record the
  deferred item and required external action in `[Done]` or the user-facing
  report. Open sections mean autonomous work remains.

## Agent State Updates

Agent state is runtime metadata at `$AGENT_ORCHESTRA_AGENT_STATE`. It may live
outside the overlay workspace, so do not use `apply_patch` for it. When your
assigned ProfessionalAgent work is ready for MainAgent review, update your own
state with a direct metadata write:

```sh
"$AGENT_ORCHESTRA_PYTHON" - <<'PY'
import json, os
from pathlib import Path

path = Path(os.environ["AGENT_ORCHESTRA_AGENT_STATE"])
data = json.loads(path.read_text(encoding="utf-8"))
data["state"] = "ready_for_review"
path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
```

Set `retired` only when MainAgent has accepted the result or explicitly retires
the ProfessionalAgent. For accepted retirement, MainAgent should write
`retired` before sending `/exit`, then verify pane cleanup and use `kill-pane`
if the pane remains. Do not leave state as `working`, `progress`, or `ready`
after reporting final scoped results unless more autonomous work remains.

## Responsibility Boundary

The task file records work state. It does not decide requirements,
architecture, implementation quality, QA verdicts, or run completion on its own.
Agents make those judgments and then update the file.
