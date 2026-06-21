---
name: agent-orchestra-task-file
description: Maintain the shared agent-orchestra task file so Hook-driven re-kick behavior follows deterministic progress/done and Backlog/InProgress/InReview/Acceptance/Gates/Candidates/Done state.
---

# agent-orchestra Task File Skill

Use this Skill when updating the shared task file for an agent-orchestra run.
The task file is the deterministic source for whether MainAgent should be
re-kicked after stopping.

## Shape

The low-level runtime can initialize a quiet empty task file with
`[status] done` for backward compatibility, but a MainAgent run that is
receiving a user task starts and stays `[status] progress` until the first
Acceptance/Gates ledger exists and all work is truly resolved. Once an Agent
accepts a user task or begins discovery, investigation, implementation, or
review work, it must keep `[status] progress` before doing substantial work.

```ini
[status]
progress

[Backlog]

[InProgress]

[InReview]

[Acceptance]

[Gates]

[Candidates]

[Done]
```

`[status]` is either `progress` or `done`.
Newly initialized task files include `[Acceptance]` and `[Gates]`. Legacy task
files that omit those two sections are parsed as empty acceptance/gate ledgers
for backward compatibility; do not "fix" that compatibility by making old task
files invalid.

Open work is any item in `[Backlog]`, `[InProgress]`, or `[InReview]`.
`[Done]` does not count as open work.

## Update Rules

- Add newly discovered work under `[Backlog]`.
- Move active work from `[Backlog]` to `[InProgress]`.
- Move work awaiting Team or peer review to `[InReview]`.
- Move accepted work to `[Done]`.
- Preserve existing run-level `[Acceptance]`, `[Gates]`, and `[Candidates]`
  entries when adding or updating scoped work. Do not replace the shared task
  file with a narrower review-only, specialist-only, or cycle-only ledger.
- Before every write, re-read the current shared task file and merge your scoped
  change into the latest `[Acceptance]`, `[Gates]`, `[Candidates]`, and open
  work sections. Do not write from a stale captured copy. If another Agent's
  item disappears or reverts after your edit, treat that as a task-file merge
  race: re-read, restore the other Agent's latest state, record the race as a
  `[Candidates]` issue, and retry the minimal scoped update.
- Never "simplify" the shared file by regenerating it from your local notes.
  Update only the lines or section entries you own, then immediately re-read the
  file to verify that unrelated acceptance, gate, candidate, and peer state
  entries survived.
- Set `[status]` to `progress` whenever open work exists or discovery is still
  active.
- Set `[status]` to `done` only after `[Backlog]`, `[InProgress]`, and
  `[InReview]` are empty; every `[Acceptance]` item is satisfied,
  out-of-scope, or deferred with required fields and evidence; every `[Gates]`
  item is passed or not-applicable with evidence; and every `[Candidates]` item
  has a completed disposition.
  `blocked` and `needs_user` are documented non-completion states. They keep
  `[status] progress` until the external action is resolved or the item is
  explicitly moved out of scope.
- Finalize in this order: first move accepted or deferred items out of open
  sections, then verify `[Backlog]`, `[InProgress]`, and `[InReview]` are empty,
  then verify `[Acceptance]`, `[Gates]`, and `[Candidates]`, and only then write
  `[status] done`.
- When review evidence shows zero remaining issues, finalization must be the
  next state update. Move accepted review items from `[InReview]` to `[Done]`,
  resolve the run-level `[Acceptance]`, `[Gates]`, and `[Candidates]` ledgers
  with evidence, then write `[status] done` in the same update pass. Do not
  leave a finalizable task file at `[status] progress` waiting for another wake,
  peer nudge, or user reminder.
- Never write `[status] done` while any real open item remains. `done` with
  open work or unresolved acceptance, gates, or candidates is a Hook re-kick
  condition, not a normal intermediate state.
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

## Acceptance Ledger

Use `[Acceptance]` to trace user/spec obligations. Each item uses:

```ini
REQ-001: status=open; source=user-prompt; owner=main; verification=planned-check; evidence=pending
```

Allowed statuses are `open`, `satisfied`, `blocked`, `needs_user`,
`out-of-scope`, and `deferred`. A finalizable item must have a non-empty id
before `:`, `status`, `source`, `owner`, `verification`, and `evidence`, and its
status must be `satisfied`, `out-of-scope`, or `deferred`. `open`, `blocked`,
`needs_user`, missing required fields, duplicate item ids, duplicate field keys,
or unknown statuses are finalization blockers. Item ids are case-insensitive for
duplicate detection; update an existing id in place instead of adding another
line with the same id.

## Gates Ledger

Use `[Gates]` for required quality gates:

```ini
gate-visual: status=open; kind=visual; evidence=pending
```

Allowed statuses are `open`, `passed`, `failed`, `blocked`, `needs_user`, and
`not-applicable`. Allowed kinds are `visual`, `mcp`, `env`, `test`, and `e2e`.
`passed` and `not-applicable` resolve a gate when the id, status, kind, and
evidence are present. `open`, `failed`, `blocked`, `needs_user`, missing
required fields, duplicate item ids, duplicate field keys, unknown statuses, or
unknown kinds are finalization blockers. Item ids are case-insensitive for
duplicate detection; replace the prior gate line rather than appending a
contradictory `passed` line beside an `open` or `failed` line.
For `kind=visual`, `status=passed` additionally requires evidence containing
URL, requested viewport, measured viewport, screenshot, console, network,
artifact directory, fit assertion, and verifying Agent details. The requested
viewport or environment set must come from the user, Spec, UI/design docs,
target platform, or existing product support scope. If none is specified, the
Agent must derive the primary verification environment from the product's
documented or implemented use case and record that rationale in evidence.
Desktop, mobile, responsive, or other platform coverage is mandatory only when
required; out-of-scope platform coverage belongs in `[Candidates]` as deferred
or rejected, not in `[Gates]`.
The measured viewport must
match the requested viewport evidence. Passed visual gates also need
server manifest or equivalent base_url/PID/log evidence, semantic assertions for
required UI states, and cleanup evidence for any dev server started by the run.
The URL/base_url in evidence must identify the same server used for screenshots,
API probes, and network logs. Stale localhost ports, requested/measured viewport
mismatches, workspace-only MCP output, or mismatched harnesses keep the gate
unresolved.

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
For AgentOrchestra runtime, launch, MCP, tmux delivery, visual-tooling, or
coordination defects observed during an E2E run, `integrated` means a
corresponding AgentOrchestra code/configuration/contract fix was actually made
and later verification proved the defect no longer recurs. For live delivery,
ProfessionalAgent retirement, session-boundary, MainAgent self-exit, or
completion-status defects, that verification must be a later clean live E2E;
focused unit regressions can support the fix but cannot convert the same run to
zero-issue or `integrated`. A current-run workaround, such as disabling MCP
inheritance for a ProfessionalAgent, bypassing a failed pane, or having
MainAgent perform a QA gate, is evidence that the product task can continue; it
is not enough evidence for `integrated`.

## Agent State Updates

Agent state is runtime metadata at `$AGENT_ORCHESTRA_AGENT_STATE`. It may live
outside the overlay workspace, so do not use `apply_patch` for it. Do not add a
`status` key to state JSON; the only completion field the runtime reads is
canonical `state`. When your assigned ProfessionalAgent work is ready for Team
review, update your own state through the runtime helper so agent id, kind, and
tmux target are preserved and stale keys are dropped:

```sh
"$AGENT_ORCHESTRA_PYTHON" -m agent_orchestra_minimal.agent_state_update \
  --state-file "$AGENT_ORCHESTRA_AGENT_STATE" \
  --state ready_for_review
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
