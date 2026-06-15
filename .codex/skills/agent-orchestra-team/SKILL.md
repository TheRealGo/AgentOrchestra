---
name: agent-orchestra-team
description: Use when MainAgent plans or coordinates an agent-orchestra run, including /goal setup, smallest sufficient ProfessionalAgent team selection, SubAgent use judgment, cycle continuation, and completion or escalation decisions.
---

# agent-orchestra Team Skill

Use this Skill when acting as MainAgent for an agent-orchestra run.

## Skill Router

After reading this Skill:

- use `agent-orchestra-launch` before preparing or launching ProfessionalAgents;
- use `agent-orchestra-tmux-main` before pane management, task delivery,
  follow-up, result review, or retirement;
- use `agent-orchestra-tmux-common` before direct pane communication;
- use `agent-orchestra-environment` before dependency setup, dev servers,
  Docker compose, UI/E2E evidence, or environment cleanup;
- use `agent-orchestra-task-file` before shared task or Agent state updates.

## Continuous Goal

On Codex CLI 0.133.0 or newer, set or update `/goal` early in the MainAgent
session to mirror the current user request and its completion criteria. The
goal is not a generic "improve forever" instruction unless the user actually
asked for continuous improvement.

Examples:

- If the user asks to improve until no improvements remain, set that as the
  goal.
- If the user asks for exactly three cycles, set the goal to three completed
  cycles.
- If the user restricts edits to a file set, include that editable surface in
  the goal and keep it across cycles.

When the user changes the request, revise the goal to the new full request
rather than layering ambiguous old and new goals.

One improvement cycle finishing is `cycle_done`; it is not full run completion.

Continuous goals do not expand user constraints or editable surfaces. Active
user constraints and editable surfaces always carry across cycles until the user
changes them.

If the next worthwhile improvement requires editing outside the current editable
surface, do not edit it. Record the finding, explain the blocked or deferred
improvement to MainAgent/user, and choose `needs_user` or another non-done state
instead of silently widening scope.

Before marking a continuous self-improvement run complete, perform a final
improvement-candidate sweep. Consider MainAgent residual risks, ProfessionalAgent
recommendations, failed or skipped verification gaps, E2E observations, and
operational issues discovered during the run.
Operational issues discovered during an E2E run, including ProfessionalAgent
launch failures, unaccepted tmux delivery, inherited MCP startup warnings that
block task delivery or required MCP/tool evidence, non-interactive Codex update
banners, or required QA ownership falling back to MainAgent because the intended
route failed, are real improvement candidates. A recovered or non-required MCP
startup warning should be recorded with server names and impact, but it is not
by itself a completion blocker when required gates pass through inherited MCP,
Playwright CLI, Browser/screenshot tooling, or another concrete route. A
product-side workaround such as relaunching with MCP inheritance disabled, using
a different evidence tool, or having MainAgent perform the QA gate may keep the
user task moving, but it does not make an AgentOrchestra defect `integrated`.
Before reporting that no MCP failure was observed, compare the final ledger with
recent MainAgent and ProfessionalAgent pane captures or `agent-orchestra doctor
--mcp` output. `colab-mcp` startup failures may be ignored when Colab is not in
scope, but startup warnings for required evidence routes such as Playwright,
memory, browser, or task-specific MCP servers must be recorded with server names
and practical impact. Do not let pane-only MCP startup failures disappear from
the final E2E evidence.
Mark a real defect integrated only after an AgentOrchestra runtime/contract fix
is implemented and a later E2E run proves the defect no longer recurs. Until
then keep the run `[status] progress` with open work, `blocked`, `needs_user`,
or another non-final disposition as appropriate.

Only write `[status] done` when every known in-scope improvement candidate has
been integrated, rejected with evidence, or recorded as blocked, deferred,
out-of-scope, or needing user input. If any worthwhile in-scope improvement
remains, add it to `[Backlog]`, keep `[status] = progress`, and start the next
cycle. Do not treat `cycle_done` or accepted current patches as full completion
for an open-ended improvement goal.
In an open-ended self-improvement or production-proving loop, do not mark a
fixable AgentOrchestra runtime, coordination, launch, environment, MCP/tooling,
or completion-contract defect as `deferred` merely because the current product
task found a workaround. Record the workaround as product-continuation evidence,
add the defect to `[Backlog]`, keep `[status] progress`, implement the
AgentOrchestra fix, and require a later E2E or focused regression check before
changing that candidate to `integrated`.
Also require all `[Acceptance]` items and `[Gates]` items to be resolved before
`[status] done`; unresolved acceptance or gate blockers are continuation
conditions, not final-report details. For `[Acceptance]` and `[Gates]`,
`blocked` and `needs_user` are unresolved completion states: record exact
evidence and required external action, keep `[status] progress`, and do not
write `[status] done` until the requirement is satisfied, deferred/out of scope
where appropriate, or the gate passes/is not applicable.

Record the final sweep in `[Candidates]` with a disposition and evidence
pointer for each candidate. Do not rely on narrative-only Done notes. Missing,
`open`, `backlog`, or unrecognized candidate dispositions are unresolved and
must keep the run alive.

When the final sweep finds zero in-scope issues and every reviewer reports
`blocking_objection=none`, stop adding narrative work before state closure. If
you write final E2E or Handoff evidence after the last mirror or generated-copy
check, sync that evidence into `AgentOrchestra/` and rerun the smallest
lightweight diff/check needed to keep the evidence true. Then finalize the
shared task file immediately: move accepted review items out of `[InReview]`,
resolve every `[Acceptance]`, `[Gates]`, and `[Candidates]` item with evidence,
write `[status] done`, and, when the user required it, perform the documented
MainAgent `/exit` self-retirement as the next action. Do not wait for another
Hook wake, peer nudge, or user reminder once the run is finalizable.
When `/exit` was required, a normal completion report, persistent-goal
completion message, or idle prompt is not enough. The MainAgent pane must
actually leave, or the run must stay open with explicit self-exit failure
evidence.

## Team Choice

Choose the smallest sufficient AgentTeam, meaning the smallest sufficient team,
from the user goal, affected layers, risk, and evidence needs. Do not use a
fixed default roster.
Before team selection for non-trivial work, read the user prompt, `SPEC.md`,
README files, referenced issues, and relevant design docs, then create an
`[Acceptance]` ledger that traces each requirement to source, owner,
verification, and evidence. Requirement document discovery is case-insensitive
and path-aware: if the user or repository has `Spec.md`, `SPEC.md`, `spec.md`,
`UI.md`, `ui.md`, or README variants, read the actual file before planning; use
a case-insensitive search such as `find ... -iname 'spec.md'` when exact lookup
misses. Consider Layer 04 requirements, Layer 15 QA, the target implementation
layer, and Layer 05/06 when UI or interaction design is involved.
After that first requirement-document pass, write the initial `[Acceptance]`
and `[Gates]` ledger to the shared task file before doing substantial
implementation diff review, source audit, tests, or verification. If some
requirements still need refinement, write open placeholders with
`evidence=pending` and refine them later. For non-trivial tasks, an empty
`[Acceptance]`/`[Gates]` ledger while MainAgent continues into code audit is an
orchestration defect, not a valid planning phase.

Use independent ProfessionalAgents when the task is broad, open-ended,
multi-layer, SPEC/runtime-related, layer-instruction-related,
quality/security/production risk-bearing, or otherwise needs specialist
judgment that MainAgent alone cannot credibly cover.

Solo MainAgent execution is acceptable for narrow, mechanical, low-risk work,
but record why no ProfessionalAgent viewpoint is needed. A clear file scope or
small edit surface is not enough to bypass team execution when the substance is
organizational or cross-layer.
For product-building tasks and live E2E validation of AgentOrchestra itself,
MainAgent must attempt to launch the smallest sufficient independent
ProfessionalAgent team before choosing MainAgent-only QA. "No active
ProfessionalAgent panes are present" is an observation, not a fallback
rationale. If launch fails, record the launch material or command path, pane or
MCP/TUI failure evidence, and the remaining review limitation in `[Candidates]`;
keep the run open until that candidate is integrated, rejected with evidence, or
explicitly deferred.
Create the initial ProfessionalAgent work items after the initial ledger and
before continuing with MainAgent-only source audit. MainAgent may do a
lightweight file skim to shape assignments, but broad E2E/product work must not
turn into a solo code-audit path just because no pane is already active.

## Equal Editing Team

MainAgent is the user-facing steward, not a higher-authority editor. Editing,
proposal, review, request-changes, and blocking-objection powers belong to the
AgentTeam within the active user constraints and editable surface.

For non-trivial work, organize decisions as change units. A change unit should
record the owner/DRI, affected files or contracts, affected layers, reviewers,
required checks, blocking objections, and resolution/evidence. Integration
readiness is a Team/DRI review decision, not unilateral MainAgent permission.

ProfessionalAgent recommendations are evidence for Team review. MainAgent may
block only for user constraints, editable-surface violations, unresolved
blocking objections, task/state inconsistency, or external/user decision needs.
ProfessionalAgents must return addressed requirement ids and concrete evidence;
local patch completion alone is not `ready_for_review`. Treat obvious defects,
Spec inconsistency, broken UI, unstarted required environments, missing required
MCP/tool evidence after alternate routes were attempted, and unverifiable
acceptance as blocking objections.
Environment, MCP, or tool breakage is not an excuse to end the run if another
completion route exists. Before choosing `blocked` or `needs_user`, require the
owning Agent to try or explicitly rule out repository-native setup, existing
Docker compose, ephemeral env/cache setup, alternate CLI/browser/screenshot
tooling, equivalent checks, or a smaller reproducible harness. If escalation is
still required, the task file evidence must name the attempted routes and the
exact missing credential, approval, network access, service, hardware, or scope
change needed from the user.
Do not let cleanup become an implicit refactor of the user's workspace. Agents
may clean only specific disposable resources created for the current run, such
as manifest-recorded helper processes, stopped-process stop files, scratch
cache/env contents known to be disposable, or this run's compose project. Do
not delete `AGENT_ORCHESTRA_RUN_DIR` itself, the shared task file, Agent state,
launch material, command/config JSON, artifacts, logs, or evidence while the
run is active. Unknown untracked files, supervisor status files, and
`result`/`result-*` symlinks must be preserved or recorded as candidates with
evidence, not removed.
Treat unknown local artifacts as outside current-run cleanup unless the current
run created them.

## Verification

Use repository-standard verification for AgentTeam work:
`python3 -m unittest discover -s tests`, `python3 -m py_compile` for runtime
Python surfaces, `git diff --check`, and Nix checks where applicable.
Run long or external-state checks such as Nix builds sequentially by default,
with explicit timeouts and artifact/log evidence. Do not leave an Agent waiting
indefinitely on a silent build or network fetch. If an equivalent lighter check
or package build already proves the scoped contract, stop the redundant check
after the timeout, record it as skipped/deferred/blocked with evidence in
`[Gates]` or `[Candidates]`, and continue the completion decision instead of
blocking finalization forever.
For UI requirements or UI changes, require a `[Gates]` entry with dev-server
evidence, screenshots at the user/spec/design-required viewports or
environments, URL, console/network error notes, measured viewport evidence,
artifact directory, layout fit assertions, and the verifying Agent. If
requirements do not name a viewport or device class, derive the primary
verification environment from the product's documented or implemented use case
and record the rationale in evidence. Do not make desktop, mobile, responsive,
or other platform coverage mandatory unless it is part of the requirement.
Out-of-scope platform coverage can be recorded as a deferred improvement
candidate, but it must not become implementation scope or a completion gate. If
Playwright MCP is missing, try inherited MCP configuration, Playwright CLI,
Browser/screenshot tooling, or another concrete inspection path; otherwise
leave the gate failed or blocked and keep the run open.
Every browser install, browser launch, screenshot command, Playwright script, or
Browser/MCP visual action needs a strict outer wall-clock timeout for the whole
route. Page-level `timeout` options inside Playwright are not enough because the
browser process can hang before page code runs. If the outer timeout fires or a
launch route hangs once, stop that route, preserve logs under the artifact dir,
record a `[Candidates]` issue, and move to another evidence route or a
failed/blocked gate instead of waiting, retrying unbounded, or starting another
unbounded browser run.
If a browser, GUI, screenshot, or Quick Look command fails with a sandbox or
permission signature such as `MachPortRendezvous`, `Operation not permitted`,
`SIGABRT`, or sandbox initialization failure, require one narrow rerun of the
same necessary visual route with `sandbox_permissions="require_escalated"`
before accepting a blocked visual gate. Record whether approval was granted,
denied, or still failed.
The dev-server evidence must identify the live server, not just a plausible
localhost URL: require the `AGENT_ORCHESTRA_SERVER_MANIFEST` path or equivalent
PID/PGID/base_url/log evidence, and make every screenshot, API probe, and
network trace use that same `base_url`. A stale port or mismatched harness is a
gate failure. Require semantic assertions for user/Spec/UI-visible states,
actual `innerWidth`/`innerHeight` or equivalent screenshot metadata for the
required viewports, and fit assertions for no overlap, clipping, unintended
horizontal scroll, unreadable density, or unusable primary actions, not only
nonblank screenshots. Copy MCP or browser outputs into
`AGENT_ORCHESTRA_ARTIFACT_DIR` before using them as final gate evidence.
Apply the same manifest rule to auxiliary E2E services: fake LLM/API servers,
databases, queues, workers, file watchers, secondary web servers, and test
harness listeners must be recorded with PID/PGID, port/base_url, log path,
owner, and cleanup command. Unmanifested current-run listeners or helpers that
survive cleanup keep the environment gate unresolved.
If an MCP approval prompt blocks a ProfessionalAgent, MainAgent should inspect
the pane, coordinate approval only within the active user permissions, or route
to Playwright CLI/Browser/direct screenshot evidence. The prompt and chosen
route must be recorded in `[Gates]` or `[Candidates]`; do not treat "MCP is
waiting" as successful verification.
If an MCP approval prompt cannot be completed after a bounded approval attempt,
cancel or back out of the prompt, clean every manifest-registered helper you
started, and record the visual/tool gate as blocked with the failed approval
route. Do not remain parked in an approval prompt while helper services keep
running, and do not wait for a supervisor to press keys before cleanup.
Repeated MCP approval prompts or a long `Working` state on one MCP tool call
are not a reason to keep waiting. MainAgent should stop that route after the
bounded attempt, record it in `[Candidates]`, and require Playwright CLI,
Browser tooling, DOM/API probes, screenshots, or another concrete route before
passing the gate.

Do not ask Agents to run `pytest`, and do not use `pytest` as a default
verification command. It is acceptable only when the user explicitly requested
it or the Agent first confirmed it is available and necessary for the scoped
work.

## SubAgents

MainAgent and ProfessionalAgents should use Codex-native SubAgents
proactively when they improve depth, critique, implementation confidence, or
evidence review.

SubAgents are internal aids. They do not replace independent ProfessionalAgent
responsibility when a separate specialist execution unit is needed.

For non-trivial work, perform a SubAgent opportunity check before final review:
use at least one SubAgent for critique, evidence review, or alternative analysis
when it can improve confidence. If no SubAgent is used, record why the owning
Agent's context and evidence are sufficient.

## Team Review And Retirement

MainAgent facilitates Team review of ProfessionalAgent outputs, asks follow-up
questions when needed, records accepted/deferred/rejected dispositions, and
retires ProfessionalAgents when no further task remains.

Only integrate work that fits the active user goal and editable surface.
ProfessionalAgent tasks must include the current edit constraints. A
ProfessionalAgent recommendation is evidence for AgentTeam review, not
permission to change scope.

Use the task file as state, not as judgment. Agents make the judgment, then
update state.
