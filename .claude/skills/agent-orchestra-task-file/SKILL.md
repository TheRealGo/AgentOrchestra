---
name: agent-orchestra-task-file
description: Maintain the shared agent-orchestra task file so Hook-driven re-kick behavior follows deterministic progress/done and Backlog/InProgress/InReview/Candidates/Done state.
---

# agent-orchestra Task File Skill

Use this Skill when updating the shared task file for an agent-orchestra run.
The task file is the deterministic source for whether MainAgent should be
re-kicked after stopping.

## Shape

The runtime initializes a quiet empty task file with `[status] done`. Once an
Agent accepts a user task or begins discovery, investigation, implementation,
or review work, it must switch the file to `[status] progress` before doing
substantial work.

```ini
[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]

[Done]
```

`[status]` is either `progress` or `done`.

Open work is any item in `[Backlog]`, `[InProgress]`, or `[InReview]`.
`[Done]` does not count as open work.

## Update Rules

- Add newly discovered work under `[Backlog]`.
- Move active work from `[Backlog]` to `[InProgress]`.
- Move work awaiting Team or peer review to `[InReview]`.
- Move accepted work to `[Done]`.
- Set `[status]` to `progress` whenever open work exists or discovery is still
  active.
- Set `[status]` to `done` only after `[Backlog]`, `[InProgress]`, and
  `[InReview]` are empty and every `[Candidates]` item has a completed
  disposition.
- Finalize in this order: first move accepted or deferred items out of open
  sections, then verify `[Backlog]`, `[InProgress]`, and `[InReview]` are empty,
  then verify the `[Candidates]` ledger, and only then write `[status] done`.
- Never write `[status] done` while any real open item remains. `done` with
  open work or unresolved candidates is a Hook re-kick condition, not a normal
  intermediate state.
- Do not stop, mark a goal `blocked`, or leave the run awaiting Hook wake while
  `[Backlog]`, `[InProgress]`, or `[InReview]` contains work the AgentTeam can
  still advance.
- If work cannot be advanced because it requires user input or an external
  state change, remove it from open sections before stopping and record the
  deferred item and required external action in `[Done]` or the user-facing
  report. Open sections mean autonomous work remains.
- `[InReview]` is not MainAgent-only. It can represent peer review,
  request-changes, blocking-objection resolution, or change-unit DRI review.
- When a review item includes a blocking objection, record the issuer, scope,
  reason, required resolution evidence, and disposition in the task text or a
  shared decision log before moving it to `[Done]`.

## Candidate Ledger

Use `[Candidates]` for final improvement-candidate sweep evidence. Candidate
items use this compact shape:

```ini
candidate-id: disposition=open; summary=short finding; evidence=path-or-pane
```

Candidate ids must be unique. Candidate field keys such as `disposition`,
`summary`, and `evidence` must not be duplicated; duplicate keys make the
candidate unresolved instead of letting later values override earlier evidence.
Every completed candidate must include a non-empty id before `:`, a completed
`disposition`, a `summary`, and an `evidence` pointer.

Completed dispositions are `integrated`, `rejected`, `deferred`, `blocked`,
`out-of-scope`, and `needs_user`. Missing, `open`, `backlog`, or unrecognized
dispositions are unresolved. If `[status]` is `done` while any candidate is
unresolved, the Stop Hook should wake MainAgent to continue or correct the
finalization.

The Hook wake carries no reason, so a malformed candidate can re-kick forever:
if `[status]` is `done`, `[Backlog]`, `[InProgress]`, and `[InReview]` are
empty, and the wake keeps repeating, the cause is an unresolved `[Candidates]`
entry — re-read every candidate line. The most common defect is a near-miss
format: a disposition written as `disposition: integrated` (colon) or a bare
`integrated` instead of `disposition=integrated`, an unrecognized disposition
word, a duplicated field key, or a missing `summary=`/`evidence=`. All of these
are treated as unresolved. Correct the line to the exact
`candidate-id: disposition=<completed>; summary=...; evidence=...` shape;
re-reporting "no open work" without fixing the format leaves the state
unchanged and makes the wake repeat without converging.

## Agent State Updates

Agent state is runtime metadata at `$AGENT_ORCHESTRA_AGENT_STATE`. It may live
outside the workspace, so do not edit it with the Edit/Write file tools. When
your assigned ProfessionalAgent work is ready for Team review, update your own
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
