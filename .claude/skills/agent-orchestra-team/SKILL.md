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
- use `agent-orchestra-task-file` before shared task or Agent state updates.

## Continuous Goal

Early in the MainAgent session, set or update `/goal` to mirror the current
user request and its completion criteria. The goal is not a generic "improve
forever" instruction unless the user actually asked for continuous improvement.

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

Only write `[status] done` when every known in-scope improvement candidate has
been integrated, rejected with evidence, or recorded as blocked, deferred,
out-of-scope, or needing user input. If any worthwhile in-scope improvement
remains, add it to `[Backlog]`, keep `[status] = progress`, and start the next
cycle. Do not treat `cycle_done` or accepted current patches as full completion
for an open-ended improvement goal.

Record the final sweep in `[Candidates]` with a disposition and evidence
pointer for each candidate. Do not rely on narrative-only Done notes. Missing,
`open`, `backlog`, or unrecognized candidate dispositions are unresolved and
must keep the run alive.

## Team Choice

Choose the smallest sufficient AgentTeam, meaning the smallest sufficient team,
from the user goal, affected layers, risk, and evidence needs. Do not use a
fixed default roster.

Use independent ProfessionalAgents when the task is broad, open-ended,
multi-layer, SPEC/runtime-related, layer-instruction-related,
quality/security/production risk-bearing, or otherwise needs specialist
judgment that MainAgent alone cannot credibly cover.

Solo MainAgent execution is acceptable for narrow, mechanical, low-risk work,
but record why no ProfessionalAgent viewpoint is needed. A clear file scope or
small edit surface is not enough to bypass team execution when the substance is
organizational or cross-layer.

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

## Verification

Use repository-standard verification for AgentTeam work:
`python3 -m unittest discover -s tests_claude`, `python3 -m py_compile` for
runtime Python surfaces, `git diff --check`, and the Nix
`claude-source-contract` check where applicable.

Do not ask Agents to run `pytest`, and do not use `pytest` as a default
verification command. It is acceptable only when the user explicitly requested
it or the Agent first confirmed it is available and necessary for the scoped
work.

## SubAgents

MainAgent and ProfessionalAgents should use Claude Code subagents (the
Task/Agent tool, `.claude/agents`) proactively when they improve depth,
critique, implementation confidence, or evidence review.

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
