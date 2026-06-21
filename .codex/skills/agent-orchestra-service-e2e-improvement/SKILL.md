---
name: agent-orchestra-service-e2e-improvement
description: Use when running AgentOrchestra against a real service such as ToO or AgenticRAG, where codex-o must improve the service while CAO primarily records observations, separates service defects from AgentOrchestra defects, avoids steering the run, and keeps status progress until a zero-issue E2E or a justified terminal stop.
---

# AgentOrchestra Service E2E Improvement

Use this Skill for production-like E2E runs where AgentOrchestra is tested by
making a real service better.

## Roles

- User: service owner and final source of service intent.
- Service Planner: supplies the service plan and service quality criteria.
- AgentOrchestra CAO: owns AgentOrchestra quality as an observer/recorder of
  codex-o behavior.
- codex-o: the AgentOrchestra MainAgent/AgentTeam that implements service work.

CAO is not a product co-pilot. After the initial plan delivery, CAO records
what AgentOrchestra does and does not do. Repeated "continue with P0/P1",
priority, handoff, or implementation-detail prompts are interventions, not
normal supervision. Each intervention is evidence that AgentOrchestra did not
autonomously maintain the run and must be recorded as an AgentOrchestra defect.

In service E2E, do not expect Orchestra to raise AgentOrchestra improvement
proposals by itself. codex-o's primary job is to complete the service. CAO owns
AgentOrchestra quality by observing the run and identifying AgentOrchestra
defects or missing mechanisms. Do not stop an in-progress service E2E just
because an AgentOrchestra improvement has been noticed. Record the defect and
continue observing unless the service run has naturally completed, is truly
terminally blocked, or needs an exceptional recovery action to prevent work
loss.

## Start Conditions

Do not instruct codex-o until the Product Planner plan or equivalent product
brief has arrived.

Create a local status file for the E2E with exactly one of:

- `progress`
- `done`

For service E2E runs that are intended to test AgentOrchestra autonomy, create
the status file inside the target service repo at:

`<service>/.tmp/agent-orchestra-service-e2e/status`

When this marker exists, AgentOrchestra launch material uses Codex
`--ask-for-approval never` with workspace-write sandboxing. This is deliberate:
low-risk local browser/mobile/iOS verification reruns and run-scoped cleanup
must not stop on CAO approval prompts. If sandboxed execution cannot complete
the required evidence, codex-o must use project-local alternatives, record the
failed route, or ask a concrete true UserNeeded question; it must not park on a
generic approval prompt.

Keep it `progress` while any service E2E issue or AgentOrchestra E2E issue
remains unresolved.

## Send The Plan

Send the full product plan to codex-o as a single confirmed delivery. Do not
summarize away completion criteria, forbidden approaches, required evidence, or
platform requirements.

The single initial instruction must say:

- complete the product, not just local patches;
- read the service SPEC/design/docs/issues/actual app behavior;
- create Acceptance/Gates before claiming completion;
- keep working or ask the user explicitly when an external credential, device,
  approval, hardware, or scope decision is truly required;
- do not use fake fallback or "worked-looking" substitutes for required core
  functionality;
- collect real evidence: tests, screenshots, browser/device/API/log evidence,
  and failure logs as required by the product plan.

## Monitoring

Use bounded checks. Constant polling is not required, but silence while codex-o
is stopped, waiting for approval, stuck at a composer, or blocked on a user
question is a CAO failure. Bounded checks must be observational by default:
capture session/window/pane state, classify it, and record defects. Do not keep
the run moving by repeatedly sending product task instructions.

On each check, classify state:

- working normally;
- multiple MainAgent panes/windows for the same run or workspace;
- visibly `Working` with no substantive output change across a bounded
  liveness sample;
- waiting for approval or user input;
- stopped with open work;
- stopped at a state that should still be autonomously recoverable;
- terminally complete or terminally blocked;
- ProfessionalAgent pane left open or unmanaged;
- delivery failed or text remains in composer;
- external blocker is real and explicitly stated;
- completed with evidence.

If codex-o is stopped with unresolved work, first record why autonomous recovery
failed. Do not immediately switch to self-improvement E2E. Decide whether the
service run should continue, has legitimately ended, or needs user/external
action. Wake, approve, or relaunch only when the stop is not a valid terminal
state and the minimal action is needed to preserve work or allow AgentOrchestra
to continue. Treat that wake/approval/relaunch as an AgentOrchestra defect
unless the product plan required an explicit external user action. If Stop Hook
should have recovered it but did not, record an AgentOrchestra defect.
If a pane appears `Working` but does not produce substantive output changes,
use `agent-orchestra doctor --tmux-liveness-pane <pane>` or equivalent bounded
captures. A stale Working pane must be interrupted, recovered, blocked, or
relaunched with evidence; do not keep silently polling it.

Before acting on a tmux target, inspect the whole `codex-o` session, not only a
remembered pane id. A service E2E with duplicate `main`, `main-recovery`, stale,
usage-limited, unsupported-model/400, or interrupted panes touching the same
workspace is not "working normally". Stop or quarantine stale panes only after
capturing evidence and record the duplicate-main condition as an
AgentOrchestra defect.

## Intervention Boundary

The service E2E exists to test whether AgentOrchestra completes the service
autonomously. CAO must not convert it into manual remote control. CAO is mainly
a recorder for AgentOrchestra improvement, not the service delivery engine.

Allowed CAO actions after initial plan delivery:

- observe tmux/process/task/evidence state;
- answer or route a truly external/human-required question;
- stop a clearly stale duplicate pane to prevent workspace corruption;
- perform a minimal approval or recovery action only when AgentOrchestra is
  stuck at a non-terminal state that should still continue;
- preserve existing evidence without creating substitute product handoff
  artifacts.

Disallowed as routine supervision:

- telling codex-o the next product subtask after every chunk;
- repeatedly restating P0/P1 priorities to keep momentum;
- telling codex-o which files to edit or tests to run when it is not blocked;
- asking for handoff or stopping the service E2E while codex-o is still
  actively pursuing the service goal;
- creating CAO-owned service handoff artifacts and treating them as
  AgentOrchestra output;
- using CAO approval/commands as the mechanism that lets low-risk work proceed;
- treating a CAO-driven recovery as proof that AgentOrchestra worked.

When a disallowed action seems necessary to prevent loss of work, do it only as
a recovery action, log it as an AgentOrchestra autonomy defect, keep E2E status
`progress`, and add it to the next self-improvement intake. Continue the
service E2E if it is still legitimately in progress.
Routine local browser, simulator, iOS, and mobile evidence reruns are not true
UserNeeded when they are project/run scoped and required by the service gates.
Run-scoped helper process cleanup and Docker compose/container/volume cleanup
are also not true UserNeeded when process identity plus run/port ownership, or
compose project/resource-name ownership, is proven. CAO approval of those
actions is defect evidence, not successful AgentOrchestra autonomy.

## Defect Separation

Record two ledgers:

- service defects: product behavior, tests, UI, API, platform, data, privacy,
  i18n, release readiness;
- AgentOrchestra defects: bad task planning, missing user question, fake
  fallback acceptance, unmanaged panes, failed wake/restart, delivery failure,
  approval deadlock, completion with open gates, wrong target scope, excessive
  CAO intervention, duplicate MainAgent panes/windows, composer residue,
  unsupported-model/400 panes, usage-limit closure gaps, or missing
  environment autonomy.

Service defects are for codex-o to discover and address from the initial
service brief and its own ongoing inspection. Do not feed service defects back
as step-by-step prompts during a running service E2E. AgentOrchestra defects
are recorded for the next self-improvement E2E; they are not fixed in the
middle of an active service run unless the service run has reached a terminal
stop and the user or CAO explicitly chooses to switch modes.

For each AgentOrchestra defect, CAO should record:

- observed service E2E symptom;
- why this is an AgentOrchestra mechanism defect rather than only a service
  defect;
- proposed AgentOrchestra behavior change;
- files/tests/skills/specs to update;
- whether a self-improvement E2E cycle is required before returning to service
  E2E.

When the observation includes approval/UserNeeded/cleanup or CAO-intervention
cases, route the recorded brief through the copied runtime intake command
instead of leaving it as narrative-only handoff text:

```sh
agent-orchestra service-e2e-intake \
  --brief-file /path/to/service-e2e-agent-orchestra-defects.md \
  --task-file "$AGENT_ORCHESTRA_RUN_DIR/tasks.ini"
```

This intake path expands the ServiceE2E worker observations into Backlog,
Acceptance, Gates, and Candidates entries and replays the nine
approval/UserNeeded/cleanup classifications through the same autonomy and
UserNeeded policy path used by the worker decision boundary. If the intake
cannot run, keep the service E2E status `progress`, record the failed command
and brief path as AgentOrchestra defect evidence, and do not claim a zero-issue
ServiceE2E or SelfE2E result from doctor/tests alone.

Service-E2E-discovered AgentOrchestra defects are not closed merely because CAO
worked around them. They need an AgentOrchestra code/config/Skill/contract fix
and either a focused regression check or self-improvement E2E evidence.

## Mode Switching

Do not switch from service E2E to self-improvement E2E merely because CAO found
an AgentOrchestra defect. If the service E2E is still running, keep observing
and record the defect. Switch modes only after one of these is true:

- service E2E reaches a legitimate completed or terminally blocked state;
- AgentOrchestra is stuck in a non-recoverable state and further observation
  cannot make meaningful progress;
- the user explicitly directs a switch.

Before switching, record whether the service run stopped by itself or because
CAO intervened. Any CAO-created handoff or recovery is not service evidence.

## Blockers

"Environment missing" is not a stopping condition by itself. codex-o should try
repo-native setup, dependency install, dev server, Docker compose, ephemeral
cache/env directories, CLI/browser/device alternatives, or a concrete user
question.

If the product requires a real provider, token, device, signing identity,
network, or hardware, codex-o must ask for that exact item. Do not mark the
feature complete with a fake fallback.

## Completion

The E2E may become `done` only when:

- the service plan's required evidence is present or explicitly accepted as
  out-of-scope by the user;
- AgentOrchestra defects found during the run are fixed or recorded with an
  accepted disposition;
- codex-o has no unresolved Acceptance/Gates/Candidates/open tasks;
- unmanaged panes, leftover helpers, and stale sessions are cleaned or
  recorded;
- final evidence is sufficient for the user to inspect the real product state.

If codex-o proposes improvements after a zero-issue E2E, CAO decides whether
they are valid improvements or scope-creep. Accept valid improvements and rerun
E2E; reject non-improvements and stop the cycle.
