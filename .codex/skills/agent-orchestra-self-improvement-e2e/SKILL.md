---
name: agent-orchestra-self-improvement-e2e
description: Use when running AgentOrchestra self-improvement E2E from AgentOrchestra-dev, including regenerating the AgentOrchestra/ copy, launching codex-o against that copy, keeping the parent dev repo out of the Agent edit scope, monitoring completion, and applying accepted copy changes back to AgentOrchestra-dev.
---

# AgentOrchestra Self-Improvement E2E

Use this Skill whenever AgentOrchestra is tested against itself.

## Non-Negotiable Shape

The editable E2E target is the generated copy:

`${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra`

Do not run self-improvement with the parent dev repo as the target:

`${AGENT_ORCHESTRA_DEV_ROOT}`

`AGENT_ORCHESTRA_DEV_ROOT` means the local checkout of the private
AgentOrchestra development repository. Resolve it to an absolute path in the
operator shell before running the examples below; do not hard-code a
machine-specific user path in committed release docs.

The parent repo is the CAO-controlled integration surface. The AgentTeam edits
the `AgentOrchestra/` copy; CAO reviews, tests, and applies accepted changes
back to the parent repo.

Self-improvement E2E must run in a dedicated tmux session or window created for
that generated-copy run. Do not launch the self-improvement MainAgent directly
inside an active ToO CAO pane/session or any service-E2E control pane. CAO may
observe or attach from another terminal, but the AgentOrchestra `/exit` and
self-exit cleanup contract applies only to the self-improvement MainAgent pane.
Self-exit cleanup must never target or kill the CAO pane, ToO pane, or any
service-E2E controller pane; if pane identity is ambiguous, keep status
`progress` and record a SelfE2E session-boundary defect instead of exiting.

During the E2E run, CAO is primarily an observer and record keeper. Do not
steer MainAgent through implementation details, repeated priority reminders, or
step-by-step fixes. If CAO has to wake, approve, redirect, or recover the run,
record that as an AgentOrchestra autonomy defect; do not count the workaround
as evidence that AgentOrchestra completed the cycle autonomously.
If CAO approval is needed for low-risk copy-local edits inside the generated
`AgentOrchestra/` copy, record it as an autonomy blocker in `[Gates]` or
`[Candidates]` and keep `.tmp/self-improvement-e2e/status` as `progress` unless
a later regression run proves no CAO approval input was needed.

Run the self-improvement worker in its own tmux session. Never start
`python3 .codex/agent_orchestra_minimal/cli.py start ...` directly inside the
ToO CAO pane/session, because `cli.py start` replaces the current pane with
MainAgent and the final `/exit`/self-exit cleanup can close that CAO pane. The
ToO CAO pane stays alive as the supervisor; the SelfE2E worker pane lives in a
dedicated session such as `AgentOrchestra-self-e2e-YYYYMMDD-HHMMSS`.

The special CAO responsibility in self-improvement is apply-back after
AgentOrchestra has produced candidate changes in the generated copy. CAO may
apply accepted copy changes to the parent repo, reject invalid proposals, and
run verification, but should not replace the self-improvement run with direct
parent-repo implementation while the E2E is still in progress.

## Canonical User Cycle

The user-standard loop is:

1. E2E: in the self-improvement `codex-o` session, tell MainAgent:

   ```text
   SPEC.md を見て AgentOrchestra/ を改善してください。
   改善点がなくなるまで改善し続けてください。
   ```

   When the Orchestra run completes, exit with `/exit`.

2. Validity decision: CAO reviews Orchestra's improvement proposals and any
   E2E issues, decides what to accept, reject, or fix, and determines the next
   implementation policy without waiting for the user to micromanage it.

3. Implementation: CAO applies accepted AgentOrchestra changes to the parent
   `AgentOrchestra-dev` repo, verifies them, regenerates `AgentOrchestra/`, and
   recreates the `codex-o` session.

Repeat 1 -> 2 -> 3 until the first clean live E2E with zero issues. If a
zero-issue E2E still produces improvement proposals, CAO must assess them.
Reject non-improvements and stop the cycle; accept true improvements,
implement them, and run one final E2E. If that final E2E creates a new issue,
revert to the prior accepted state.

The CAO owns the cycle. Do not wait for the user to restate step 2 or approve
ordinary file edits/tests/rebuilds that are already within the granted scope.

## Service-E2E Defect Intake

When a real-service E2E exposes AgentOrchestra autonomy defects, feed those
observations into the next self-improvement cycle. Do not treat CAO workarounds
as success. The defect brief is input evidence, not a CAO-authored
implementation script. Create a concise defect brief for the generated
`AgentOrchestra/` copy covering:

- the observed service symptom;
- what CAO had to do manually;
- why codex-o/AgentOrchestra should have handled it autonomously;
- the desired runtime/Skill/contract behavior;
- the focused regression evidence expected after the fix.

Typical service-E2E autonomy defects include duplicate MainAgent windows or
panes for the same workspace, stale `main-recovery` panes, unsupported-model
400 panes, usage-limit closure gaps, composer residue, Stop Hook failure to
resume, unmanaged ProfessionalAgent panes, and CAO repeatedly sending product
next-step prompts to keep work moving.

The self-improvement prompt may include this defect brief in addition to the
canonical `SPEC.md` instruction. Do not turn the brief into detailed file-level
orders unless AgentOrchestra itself asks a legitimate clarification. The
generated copy must inspect `SPEC.md`, reason about the mechanism defects, and
improve AgentOrchestra so the same service E2E would need less CAO
intervention, not merely document the incident.

## Regenerate The Copy

Before each valid self-improvement E2E cycle:

1. Stop any stale self-improvement `codex-o` run.
2. Move the existing `AgentOrchestra/` to a timestamped backup under
   `.tmp/self-improvement-e2e/`.
3. Recreate `AgentOrchestra/` from the current parent repo, excluding `.git`,
   `.tmp`, `AgentOrchestra`, `result`, and `result-*`.
4. Create `AgentOrchestra/.tmp/self-improvement-e2e/status` with exactly
   `progress`.
5. Launch the next self-improvement `codex-o` inside a dedicated tmux session or
   window for this generated-copy run, never inside a ToO CAO/service-E2E
   controller pane. Record the self-improvement MainAgent pane id separately
   from any observer/CAO pane before sending the prompt.
6. Initialize the generated copy as its own nested Git repository baseline
   before launching `codex-o`:

   ```sh
   git -C AgentOrchestra init
   git -C AgentOrchestra add -A
   git -C AgentOrchestra -c user.name=AgentOrchestra -c user.email=agent-orchestra@example.invalid commit -m "self-improvement baseline"
   ```

   Then verify `git -C AgentOrchestra rev-parse --show-toplevel` is exactly
   the generated copy and `git -C AgentOrchestra status --short` is clean.
   This is not release history; it prevents `git status`, `git diff --check`,
   and ProfessionalAgent review commands inside the copy from walking up to
   the parent `AgentOrchestra-dev` repository and hiding copy-local edits.
7. Put the MainAgent prompt/evidence files under the copy, not only under the
   parent repo. Any copied prompt, watchdog, or handoff evidence that names the
   E2E status file must name `.tmp/self-improvement-e2e/status` from inside the
   generated copy, not the older `.codex/tmp/improvement-cycle.status` helper
   path.
7. Create a fresh dedicated tmux session for the SelfE2E worker and record both
   the CAO supervisor pane and the worker pane before sending any task:

   ```sh
   SELF_E2E_SESSION="AgentOrchestra-self-e2e-$(date +%Y%m%d-%H%M%S)"
   CAO_PANE="$(tmux display-message -p '#{pane_id}')"
   tmux new-session -d -s "$SELF_E2E_SESSION" -c "${AGENT_ORCHESTRA_DEV_ROOT:?}"
   SELF_E2E_PANE="$(tmux list-panes -t "$SELF_E2E_SESSION" -F '#{pane_id}' | head -n 1)"
   printf 'CAO supervisor pane: %s\nSelfE2E session: %s\nSelfE2E worker pane: %s\n' "$CAO_PANE" "$SELF_E2E_SESSION" "$SELF_E2E_PANE"
   ```

   The run is invalid if `SELF_E2E_PANE` is the ToO CAO pane, if the session
   name is `ToO`, `CAO`, `cao`, or `ToO-codex-o`, or if no dedicated
   `AgentOrchestra-self-e2e-*` session exists. If a previous SelfE2E was
   started from the CAO pane, treat that as an AgentOrchestra E2E procedure
   defect and fix the procedure before continuing.

## Launch Boundary Check

Launch `codex-o` inside the dedicated SelfE2E tmux session from
`AgentOrchestra-dev`, but target the copy. Paste this shell command only into
the `SELF_E2E_PANE`, not the ToO CAO pane:

```sh
python3 .codex/agent_orchestra_minimal/cli.py start \
  "${AGENT_ORCHESTRA_DEV_ROOT:?}/AgentOrchestra"
```

After launch, re-check the active worker pane and record:

```sh
tmux list-panes -t "$SELF_E2E_SESSION" -F '#{session_name}:#{window_index}.#{pane_index} #{pane_id} #{pane_current_command} #{pane_current_path}'
```

The `SelfE2E worker pane` is the pane that may receive `/exit`; the CAO
supervisor pane must not receive `/exit` and must not be killed by SelfE2E
cleanup.

Before sending the task, inspect the generated `env.json` and `command.json`.
The run is invalid if any of these are false:

- `AGENT_ORCHESTRA_TARGET_PROJECT` is the `AgentOrchestra/` copy.
- `AGENT_ORCHESTRA_EDIT_ROOT` is the `AgentOrchestra/` copy.
- Codex `--add-dir` includes the `AgentOrchestra/` copy and the run dir.
- Codex `--add-dir` does not include the parent
  `${AGENT_ORCHESTRA_DEV_ROOT}`.

If the parent dev repo appears as an edit/access root, stop the run and fix the
launch boundary before continuing. Do not paper over this by telling Agents not
to edit the parent repo.

Also verify the generated copy's Git boundary before launch. A self-
improvement E2E is invalid if `git -C AgentOrchestra rev-parse --show-toplevel`
resolves to the parent dev repo or if `git -C AgentOrchestra status --short`
shows parent paths such as `../.codex/...`. Stop, regenerate the copy with the
nested baseline, and rerun instead of relying on instruction text alone.

## MainAgent Prompt Requirements

Tell MainAgent:

- the target is the `AgentOrchestra/` copy;
- status file is `.tmp/self-improvement-e2e/status` from inside the
  `AgentOrchestra/` copy, or `AgentOrchestra/.tmp/self-improvement-e2e/status`
  from the parent CAO shell;
- improve from `SPEC.md` until no improvements remain;
- preserve and extend existing copy changes;
- use ProfessionalAgents when non-trivial;
- because the generated copy has `.tmp/self-improvement-e2e/status`, launch
  material should use Codex `--ask-for-approval never` while retaining
  `--sandbox workspace-write`, so copy-local low-risk edits do not ask CAO for
  approval;
- do not mark done while task file Acceptance/Gates/Candidates/open work remain
  unresolved;
- before claiming zero-issue completion, write `.tmp/self-improvement-e2e/status`
  to `done`, read the same file back, and record evidence that its observed
  content is exactly `done`;
- `.tmp/self-improvement-e2e/status` may be `done` only after the shared task
  file itself is finalized as `[status] done` and the status-file readback is
  exactly `done`; otherwise write/read back `progress` and record blockers;
- the final SelfE2E action should use
  `python3 -m agent_orchestra_minimal.self_e2e_finalizer`, not bare
  `agent_orchestra_minimal.self_exit`, with both
  `--status-path "${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/status"`
  and `--task-file "${AGENT_ORCHESTRA_TASK_FILE}"` so its detached child
  writes the actual result JSON first and then finalizes the copied-runtime
  status from the finalized shared task readback, reads the same file back, and
  records whether the observed content is exactly `done`;
- status `done` also requires actual copied-runtime
  `${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/main-self-exit*.json`
  readback proving `closed: true`, same-session auxiliary cleanup evidence, and
  `session_gone: true` for the dedicated SelfE2E session, with no CAO cleanup;
  expected text in the task file is not sufficient;
- status `done` also requires
  `${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/active-main-session.json`
  to bind the recorded active SelfE2E MainAgent `pane` and `session_name`; the
  final `main-self-exit*.json` must match both fields exactly, so a separate
  proof/final session cannot satisfy current-run completion;
- use `/exit` only after zero-issue finalization and `[status] done`, as the
  final orchestra action. In SelfE2E, the finalizer is the atomic handoff that
  makes the post-exit copied-runtime status readback possible.
- verify `/exit`/self-exit targets the self-improvement MainAgent pane, not a
  CAO, ToO, service-E2E, observer, or controller pane.
- for the final self-exit helper in a dedicated SelfE2E session, pass
  `--allow-shell-cleanup-session-prefix AgentOrchestra-self-e2e-` and
  `--cleanup-auxiliary-shells` only for the recorded SelfE2E worker pane so a
  post-Codex shell and same-session auxiliary shell panes can be cleaned without
  touching CAO/ToO panes. Record the resulting `auxiliary_shell_panes` and
  `session_gone` evidence
  from `${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/main-self-exit*.json`.
- required final ProfessionalAgent report delivery with degraded retries is a
  delivery-defect candidate and gate evidence; unresolved degraded delivery
  keeps the run non-zero and `.tmp/self-improvement-e2e/status` as `progress`.
- CAO will not provide routine next-step prompts; AgentOrchestra must plan,
  execute, verify, recover from ordinary fixable stops, and ask the user only
  for truly external action.

## Completion And Apply-Back

`status` remains `progress` while any E2E issue remains.

Only after the copy run reaches zero unresolved issues in a clean live E2E may
the copy write `done`. CAO then performs the validity decision, accepts or
rejects proposals, applies accepted changes to the parent dev repo, runs
verification, regenerates `AgentOrchestra/`, and starts the next E2E cycle if
needed.

If CAO intervened during the run, completion is not zero-issue unless the
intervention is either explicitly accepted as external/user-required or fixed
as an AgentOrchestra defect with regression evidence. Apply-back should preserve
that distinction: accepted code changes are not enough if the E2E only reached
them because CAO manually drove the run.
