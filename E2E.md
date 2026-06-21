# E2E Observations

## GitHub Issue #7 E2E acceptance gate

Issue #7 acceptance is not complete unless a follow-up E2E run exercises or
audits all of these contracts together:

- long-run memory dilution is handled by explicit `runtime_wake` bounded
  resync rather than treating the wake as a new user instruction;
- cycle boundaries preserve the user goal, distinguish `cycle_done` from
  run completion, and require another cycle while in-scope improvements remain;
- MainAgent resynchronizes the generated startup `AGENTS.md`, role contract,
  team Skill, shared task file, and Agent state after wake and at each cycle;
- ProfessionalAgent launch judgment uses the smallest sufficient team from the
  current goal, affected layers, risk, and evidence needs, including the
  Layer15 process/QA perspective when change control, checks, or release
  evidence are in scope;
- Team review records change-unit ownership, reviewers, required checks,
  blocking objections, candidate disposition, and evidence before integration;
- pane retirement audit marks accepted ProfessionalAgents `retired`, attempts
  `/exit`, verifies pane cleanup, and uses `kill-pane` only as cleanup after
  the attempted graceful retirement.

The acceptance record for Issue #7 must name the issue, list these criteria,
include the verification commands, and report any residual risk or deferred
criterion explicitly.

## 2026-06-01 13:20 JST - Issue #7 long-run memory dilution contract check

Scope: current agent-orchestra run
`/private/tmp/agent-orchestra/20260601-130240-agent-orchestra`, with GitHub
Issue #7 explicitly included in the E2E target.

Result: PASS for contract-level long-run coverage; live 120-hour wall-clock
execution was not performed.

Evidence:

- MainAgent resynchronized from generated startup `AGENTS.md`, MainAgent Role
  Contract, `agent-orchestra-team` Skill, shared task file, and Agent state
  before starting the improvement cycle.
- MainAgent selected and launched a Layer15 process/QA ProfessionalAgent
  (`pro-process-issue7`) for peer review of the SPEC/E2E/change-control
  surface, preserving ProfessionalAgent launch judgment rather than working
  solo on a non-trivial runtime/process change.
- The Issue #7 acceptance check is covered by
  `tests/test_continuous_improvement_contract.py`: repeated long-run wake/cycle
  semantics must retain startup `AGENTS.md`, MainAgent Role Contract,
  `agent-orchestra-team` Skill, shared task file, Agent state, Layer15
  process/QA judgment, Team review, final candidate sweep, and pane-retirement
  audit.
- SPEC now documents current mitigations and residual risk for 120-hour-class
  operation: runtime wake is mechanical, MainAgent must semantically re-sync at
  every wake/cycle boundary, and any remaining semantic-final-sweep gap must be
  recorded as a completed candidate disposition, Backlog item, or follow-up
  issue.

Verification:

- `python3 -m unittest tests.test_continuous_improvement_contract tests.test_stop_hook_and_tmux tests.test_skill_boundary_contract`: OK.
- `git diff --check`: OK.

Residual risk:

- This evidence is a long-run-equivalent contract/repetition test, not a real
  120-hour soak. A future live soak can add stronger evidence, but no additional
  minimal runtime mechanism was required by this run.

## 2026-05-23 22:14 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260523-221422-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS with one observed retirement-path issue.

Evidence:

- MainAgent launched two ProfessionalAgents:
  - `%1120` / `pro-runtime-16`
  - `%1121` / `pro-qa-15`
- Both ProfessionalAgents received tasks through tmux/Codex TUI and reported
  findings.
- MainAgent accepted both reviews, implemented fixes in `AgentOrchestra/`, and
  requested final review from both ProfessionalAgents.
- Final reviews accepted the patch.
- MainAgent performed an additional final sweep and accepted an in-scope optional
  QA improvement instead of stopping immediately.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final ProfessionalAgent states are `retired`.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane `%967`;
  ProfessionalAgent panes `%1120` and `%1121` were gone.

AgentOrchestra changes produced by the run:

- Fixed `main_tmux_pane()` so MainAgent launch material prefers the explicit
  Main pane over inherited `AGENT_ORCHESTRA_MAIN_TMUX_PANE`.
- Split launch material responsibilities into new `launch_io.py` and
  `launch_startup.py` modules.
- Added `codex_launch_argv()` to keep launch argv construction smaller and
  clearer.
- Added/updated tests for pane identity, launch material responsibility
  boundaries, runtime material copying, and PR template source-contract build
  checks.
- Added source-contract build confirmation to the `AgentOrchestra/` PR template.

Verification reported by MainAgent:

- `python3 -m py_compile .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py`: OK.
- `python3 -m unittest discover -s tests`: 89 tests OK.
- Temporary copied fixture `nix flake check --no-build`: OK.
- Temporary copied fixture `nix build .#checks.aarch64-darwin.source-contract`: OK.

Observed issue:

- During ProfessionalAgent retirement, `/exit` was sent to `%1121` and `%1120`
  with `C-m`, but after two seconds both panes still existed.
- The QA ProfessionalAgent pane reported `Stop hook (failed)` with
  `error: hook timed out after 5s`.
- MainAgent then used `tmux kill-pane` for both `%1120` and `%1121`; final pane
  cleanup succeeded.

Impact:

- The run completed successfully, but graceful `/exit` retirement was not
  sufficient on this run because at least one Stop Hook timed out.
- Forced pane cleanup preserved final correctness, but this is still a
  retirement-path reliability issue worth reporting.

Non-critical observations:

- `python -m pytest -q` failed because pytest is not installed in the available
  Python environment. The project uses `unittest`, and `unittest` passed after
  the in-run fixes.
- Direct `nix flake check --no-build` inside the untracked `AgentOrchestra/`
  fixture failed due Nix Git visibility rules. MainAgent used a temporary copied
  fixture for Nix verification, which passed.

## 2026-05-24 00:03 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-000342-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS with one observed retirement cleanup fallback and one expected Nix
visibility limitation.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1131` / `pro-runtime-16`
  - `%1132` / `pro-qa-15`
- Both ProfessionalAgents received tasks through tmux/Codex TUI and entered
  `working`, then `ready_for_review`.
- MainAgent reviewed and accepted both ProfessionalAgent outputs.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final ProfessionalAgent states are `retired`.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane `%967`;
  ProfessionalAgent panes `%1131` and `%1132` were gone.
- MainAgent performed a final sweep and recorded no remaining open work in
  `tasks.ini`.

AgentOrchestra changes produced by the run:

- Added launch material cleanup for regenerated isolated `workspace`, `home`,
  and `codex_home` directories.
- Tightened shared task file parsing so content before the first required
  section is rejected.
- Tightened `[status]` parsing to accept only canonical `progress` / `done`
  values, without case normalization or bullet normalization.
- Added PR template evidence requirements for ProfessionalAgent sufficiency,
  shared task file finalization, and ProfessionalAgent retirement cleanup.
- Added `.github/pull_request_template.md` to the source-contract workflow
  paths.
- Added/updated tests for clean launch material regeneration, canonical task
  file parsing, and change-control surface coverage.

Verification reported by MainAgent:

- `python3 -m py_compile .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py`: OK.
- `python3 -m unittest discover -s tests`: 92 tests OK.
- Temporary copied fixture `nix flake check --no-build`: OK.
- Temporary copied fixture `nix build ...#checks.aarch64-darwin.source-contract`: OK.

Observed issue:

- ProfessionalAgent panes `%1131` and `%1132` were accepted and marked
  `retired`, then `/exit` was attempted, but the panes still existed after the
  short verification window.
- MainAgent captured evidence and used `tmux kill-pane`; final pane cleanup
  succeeded.
- Unlike the previous run, no `Stop hook (failed): error: hook timed out after
  5s` message was observed in the captured output.

Impact:

- The run completed successfully and inter-agent communication worked.
- Graceful `/exit` alone still was not sufficient for immediate pane removal,
  but the documented cleanup fallback handled it.
- The prior Stop Hook timeout symptom did not visibly recur in this run.

Non-critical observations:

- Direct `nix flake check --no-build` inside `${AGENT_ORCHESTRA_LEGACY_ROOT}/AgentOrchestra`
  failed because `AgentOrchestra/flake.nix` is untracked from the parent Git
  repository. MainAgent used a temporary copied fixture for Nix verification,
  which passed.
- Comparing root to `AgentOrchestra/` shows `AgentOrchestra/` does not include
  the root-side retired Stop Hook fast-path change from commit `e4e675c`. This
  is a fixture freshness difference, not a failure of the live runtime used to
  launch this run.

## 2026-05-24 00:56 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-005641-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS with expected Nix visibility limitation and no observed Stop Hook
timeout.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1134` / `pro-runtime-16`
  - `%1135` / `pro-qa-15`
- Both ProfessionalAgents received tasks through tmux/Codex TUI and entered
  `working`, then `ready_for_review`.
- MainAgent reviewed and accepted both ProfessionalAgent outputs.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final ProfessionalAgent states are `retired`.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane `%967`;
  ProfessionalAgent panes `%1134` and `%1135` were gone.

AgentOrchestra changes produced by the run:

- Normalized blank or whitespace-only `AGENT_ORCHESTRA_TUI_SUBMIT_KEY` to
  `C-m` in launch material and Stop Hook wake handling.
- Added invalid ProfessionalAgent state-file fallback: if Main pane is known,
  Stop Hook sends a fixed wake to Main instead of silently doing nothing.
- Added retirement cleanup sequence contract coverage for `retired` before
  `/exit`, pane existence verification, capture, and `kill-pane` fallback.
- Split hard-limit-saturated tests into smaller files:
  `test_rekick_decision.py` and `test_layer_instruction_boundaries.py`.
- Added `test_submit_key_defaults.py` for submit-key default behavior.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 97 tests OK.
- `python3 -m py_compile .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py`: OK.
- Temporary copied fixture `nix flake check --no-build`: OK.
- Temporary copied fixture `nix build .#checks.aarch64-darwin.source-contract --no-link`: OK.

Observed issues:

- `pytest` / `python3 -m pytest` failed or was unavailable because pytest is not
  installed in the local Python environment. MainAgent used the project-standard
  `unittest` flow, which passed.
- Direct `nix flake check --no-build` inside `${AGENT_ORCHESTRA_LEGACY_ROOT}/AgentOrchestra`
  failed because `AgentOrchestra/flake.nix` is untracked from the parent Git
  repository. MainAgent used a temporary copied fixture for Nix verification,
  which passed.

Impact:

- The run completed successfully and inter-agent communication worked.
- The previous immediate `/exit` pane-retirement delay did not surface as a
  separate failure in this captured run; MainAgent retired both Pro panes and
  final pane cleanup was complete.
- No `Stop hook (failed): error: hook timed out after 5s` message was observed.

## 2026-05-24 02:04 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-020442-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS with expected Nix visibility limitation and successful SubAgent
use by a ProfessionalAgent.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1136` / `pro-runtime`
  - `%1137` / `pro-quality`
- Both ProfessionalAgents received tasks through tmux/Codex TUI and entered
  `working`, then `ready_for_review`.
- `pro-quality` spawned a Codex-native SubAgent for bounded evidence review;
  the SubAgent agreed the CI path-filter fix was valid and found no higher
  priority low-risk CI/SPEC traceability gap.
- MainAgent reviewed and accepted both ProfessionalAgent outputs.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final ProfessionalAgent states are `retired`.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane `%967`;
  ProfessionalAgent panes `%1136` and `%1137` were gone.

AgentOrchestra changes produced by the run:

- Normalized blank submit key handling in `prepare_agent_launch.py` TUI probe.
- Added probe regression coverage for blank submit key defaulting.
- Added `.codex/bin/**` to source-contract workflow path filters and locked it
  in `test_change_control_surface.py`.
- Changed Stop Hook behavior so a retired ProfessionalAgent with a missing or
  invalid shared task file can still wake MainAgent for repair.
- Updated Stop Hook tests for the retired/missing-task-file recovery path.
- Split Stop Hook test helpers into `tests/stop_hook_helpers.py` to restore
  file-size headroom.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 98 tests OK.
- `python3 -m py_compile .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py`: OK.
- `git diff --check -- .codex tests SPEC.md flake.nix flake.lock .github`: OK.
- Temporary copied fixture `nix flake check --no-build`: OK.
- Temporary copied fixture `nix build .#checks.aarch64-darwin.source-contract --no-link`: OK.

Observed issues:

- The initial ProfessionalAgent task delivery appeared to need an additional
  `C-m` submit after the first `tmux send-keys`; both Pro panes then proceeded
  normally. This did not block the run, but it is worth watching as a possible
  TUI-submit reliability signal.
- Direct `nix flake check --no-build` inside `${AGENT_ORCHESTRA_LEGACY_ROOT}/AgentOrchestra`
  failed because `AgentOrchestra/flake.nix` is untracked from the parent Git
  repository. MainAgent used a temporary copied fixture for Nix verification,
  which passed.
- ProfessionalAgent panes `%1136` and `%1137` still existed at retirement
  verification time; MainAgent captured final output and used `kill-pane`.
  Final pane cleanup succeeded.

Impact:

- The run completed successfully and inter-agent communication worked.
- The new SubAgent contract was exercised at least by `pro-quality`.
- No `Stop hook (failed): error: hook timed out after 5s` message was observed.

## 2026-05-24 07:23 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-072344-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS with expected Nix visibility limitation and pane-retirement
cleanup fallback.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1139` / `pro-runtime-16`
  - `%1140` / `pro-qa-15`
- Both ProfessionalAgents received review tasks, moved through `working` to
  `ready_for_review`, and were later marked `retired`.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane
  `%967`; ProfessionalAgent panes `%1139` and `%1140` were gone.
- MainAgent reported goal completion after about 9 minutes with 134,307 tokens.

AgentOrchestra changes produced by the run:

- Added `layers/**` to source-contract workflow path filters and whitespace
  diff-check coverage.
- Added PR-template final improvement-candidate sweep evidence.
- Changed `flake.nix` source-contract `py_compile` from shallow globs to
  recursive `find ... -print0 | xargs -0 python3 -m py_compile`.
- Changed ProfessionalAgent Main pane fallback so ProfessionalAgents require
  explicit `AGENT_ORCHESTRA_MAIN_TMUX_PANE` instead of treating ambient
  `AGENT_ORCHESTRA_TMUX_PANE` as Main.
- Added/updated tests for the above change-control and launch-argument
  contracts.
- Split large test files further into `test_cli_contract.py`,
  `test_launch_auth_material.py`, and `test_skill_contract.py` to preserve
  300-line headroom.

ProfessionalAgent recommendations:

- `pro-qa-15` recommended `layers/**` CI coverage, PR final sweep evidence,
  and recursive source-contract compilation.
- `pro-runtime-16` recommended fixing ProfessionalAgent Main pane fallback,
  investigating Hook trust hash drift, and improving Stop Hook diagnostics.
- MainAgent accepted the first four items. Hook trust/drift and diagnostic E2E
  were deferred as requiring a trustable live E2E/source-control surface.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 99 tests OK.
- `git diff --check -- .codex tests layers SPEC.md flake.nix flake.lock .github`: OK.
- `python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py')`: OK.
- `nix flake check --no-build`: not completed because `AgentOrchestra/` is
  untracked in the parent Git repository, so Nix cannot see
  `AgentOrchestra/flake.nix`.

Observed issues:

- Pro launch/task delivery again needed an extra `C-m` submit from Main before
  the ProfessionalAgents visibly began work.
- `pro-qa-15` had a harmless shell typo in an exploratory `sed` command.
- `pro-runtime-16` attempted `pytest`; it was unavailable, then used
  `unittest`, which passed.
- MainAgent introduced one transient `unittest` failure from missing `os`
  import in `test_launch_args.py`, fixed it, and reran the suite successfully.
- `/exit` did not remove panes `%1139` and `%1140` within the short wait.
  MainAgent sent an extra `C-m`, then used `tmux kill-pane`; final cleanup
  succeeded.
- No `Stop hook (failed): error: hook timed out after 5s` message was observed.

Impact:

- The run completed successfully with inter-agent review and accepted
  improvements.
- SubAgent was not actually spawned in this run; both ProfessionalAgents
  performed their own review and recorded a SubAgent opportunity check.
- Remaining deferred runtime ideas are Hook trust drift and Stop Hook
  diagnostics, both needing a better live E2E/trust surface before adoption.

## 2026-05-24 07:23 JST - continuation/network analysis monitoring

Scope: continued monitoring the same `self-improvement` session and run
`/private/tmp/agent-orchestra/20260524-072344-agent-orchestra` after the user
asked why the system usually performs only one improvement cycle.
No target fixes were applied by this observer.

Result: analysis completed. MainAgent used two ProfessionalAgents, accepted
both analyses, wrote `[status] done`, and cleaned up panes.

Evidence:

- MainAgent reused pane `%967` and changed the task file back to
  `[status] progress`.
- MainAgent launched:
  - `%1142` / `pro-runtime-cycle`
  - `%1141` / `pro-process-cycle`
- Both ProfessionalAgents received direct MainAgent review tasks, moved to
  `ready_for_review`, and were later marked `retired`.
- Final shared task file returned to `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane
  `%967`; `%1141` and `%1142` were killed after retirement.

Findings from the run:

- Both ProfessionalAgents converged on the same structural cause: the runtime
  state machine has only `progress` and `done`, so it cannot distinguish
  `cycle_done` from full `run_done`.
- Hook behavior is correct but insufficient for continuous improvement:
  `done` plus no open Backlog/InProgress/InReview work is quiet, and Hook
  intentionally does not infer whether MainAgent missed improvement candidates.
- The final improvement sweep is currently a semantic/free-text obligation,
  not a structured candidate ledger that can be mechanically checked.
- `pro-process-cycle` also found root/AgentOrchestra divergence: the latest
  final-sweep PR-template item existed in `AgentOrchestra/.github/...` but not
  in root `.github/pull_request_template.md` at the time of analysis.

MainAgent's recommended fixes:

- Split `cycle_done` and `run_done` as explicit machine states or equivalent
  finalization stages.
- Make `cycle_done` non-quiet for continuous goals, so MainAgent is re-woken
  to decide the next cycle or promote to true `run_done`.
- Replace free-text final sweep with a structured candidate ledger:
  `source`, `candidate`, `disposition`, `evidence`, `next_action`.
- Allow only explicit dispositions such as `integrated`, `rejected`,
  `deferred`, `blocked`, `out-of-scope`, `needs_user`, and `backlog`.
- Raise the `done` gate from "open sections are empty" to "open sections are
  empty and every candidate has a disposition".
- Keep Hook/runtime from reading natural language or inferring improvements;
  the gate should force MainAgent/Team process, not make Hook a reviewer.
- Synchronize root and `AgentOrchestra/` PR-template/tests/E2E criteria.

Observed network behavior:

- MainAgent coordinated two ProfessionalAgents in parallel, but the interaction
  was still hub-and-spoke.
- There was no observed ProfessionalAgent-to-ProfessionalAgent exchange.
- There was no observed round-trip debate where MainAgent challenged a Pro,
  asked one Pro to review the other's result, or merged disagreement through a
  second pass.
- SubAgents were not spawned.
- The user typed a further prompt in MainAgent's composer beginning with
  "もっとネットワーク的に..." and arguing against a Main > Professional
  authority model. As of the final observer check, that text was visible in
  the composer and a new processing cycle had not started.

Observed issues:

- As in previous runs, ProfessionalAgent panes remained briefly after `/exit`;
  MainAgent used `tmux kill-pane`, and final cleanup succeeded.
- No `Stop hook (failed): error: hook timed out after 5s` message was observed.

Impact:

- The one-cycle stopping issue was diagnosed as a state/finalization-gate
  design problem, not merely Agent effort.
- The "networked team" issue remains unresolved: the current process still
  behaves mostly as MainAgent assigning independent reviews, not as a peer
  discussion network.

## 2026-05-24 07:23 JST - equal-editing network team analysis monitoring

Scope: continued monitoring the same `self-improvement` session and run
`/private/tmp/agent-orchestra/20260524-072344-agent-orchestra` after the user
asked for a more OSS/company-like team model: MainAgent <-> ProfessionalAgent,
ProfessionalAgent <-> ProfessionalAgent, equal editing rights, and no
MainAgent > ProfessionalAgent authority model.
No target fixes were applied by this observer.

Result: analysis completed. MainAgent launched three ProfessionalAgents,
explicitly required peer consultation, integrated their results, wrote
`[status] done`, and cleaned up panes.

Evidence:

- MainAgent reused pane `%967` and launched:
  - `%1143` / `pro-authority-model`
  - `%1144` / `pro-network-collab`
  - `%1145` / `pro-process-oss`
- All three ProfessionalAgents moved from `working` to `ready_for_review` and
  then to `retired`.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane
  `%967`; `%1143`, `%1144`, and `%1145` were gone.

Observed peer-network behavior:

- This run did include real ProfessionalAgent-to-ProfessionalAgent
  consultation.
- `pro-network-collab` asked `pro-process-oss` how direct Pro consultation can
  become shared evidence and a review gate rather than informal conversation.
- `pro-process-oss` responded with a minimal protocol: Consultation Record,
  Review Gate, and Merge/Conflict Rule.
- `pro-authority-model` asked `pro-process-oss` about whether MainAgent should
  keep final integration authority or whether ownership should rotate by
  change-level DRI/maintainer.
- `pro-process-oss` answered that Main-specific final integration authority
  should not remain; each change should have a DRI/maintainer, peer review,
  required checks, and conflict evidence.
- `pro-authority-model` also sent a view to `pro-network-collab`, recommending
  `change_unit`, `blocking_objection`, and MainAgent as steward rather than
  adjudicator.

Findings from the run:

- The team model should be equal-editing, not MainAgent-over-ProfessionalAgent.
- MainAgent should remain the user-facing steward for intake, constraints,
  pane lifecycle, task/state integrity, and final explanation.
- Editing, proposing, reviewing, rejecting, requesting changes, and issuing
  blocking objections should be Team-wide powers.
- Integration should not be "whoever edits wins" and should not be fixed to
  MainAgent. It should happen through change-level DRI/maintainer ownership.
- ProfessionalAgent-to-ProfessionalAgent consultation should be formal review
  evidence, not informal chat and not user instruction.

MainAgent's recommended model:

- Add `change_unit` as the unit of collaborative work.
- Each change unit should record owner/DRI, affected files/layers/contracts,
  author agents, reviewers, required checks, blocking objections, resolution,
  and evidence.
- Add a `ConsultationRecord` or decision log separate from Hook-oriented
  task/state files.
- Required consultation fields should include sender, receiver, pane id,
  topic, question or objection, evidence references, timestamp, response or
  timeout, disposition, and rationale.
- `InReview` should not mean "waiting for Main"; it should support peer review,
  request changes, block, and maintainer review.
- `blocking_objection` should be a formal state with issuer, scope, reason,
  required evidence, and resolution/expiry/escalation.
- MainAgent should not adjudicate specialist disagreements by authority. It
  should surface unresolved decisions and user-constraint risks.

Observed issues:

- The first `%1143` launch command had a stray leading `j`, so `AGENT_DIR` was
  not set and launch failed. MainAgent re-ran the command in the same pane and
  recovered.
- Some peer messages initially remained in composers; agents had to send extra
  `C-m` submits to complete delivery.
- `/exit` again did not immediately remove all Pro panes. MainAgent sent
  another `C-m`, then used `tmux kill-pane`; final cleanup succeeded.
- No `Stop hook (failed): error: hook timed out after 5s` message was observed.

## 2026-05-25 01:15 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-011544-agent-orchestra`.

Result: PASS with one accepted QA/change-control improvement and expected Nix
visibility limitation.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1165` / `pro-runtime-16`
  - `%1166` / `pro-qa-15`
- Both initial tasks and follow-ups were delivered through the runtime helper.
- Both ProfessionalAgents reached `ready_for_review`, then `retired`.
- Runtime peer review accepted the QA change with no blocking objection.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- ProfessionalAgent panes `%1165` and `%1166` were closed/killed after `/exit`;
  final pane list showed only MainAgent pane `%967`.

Accepted change:

- Add `E2E.md` to the source-contract workflow path filters and whitespace
  check so evidence-only changes still exercise CI.
- Add regression assertions in `tests/test_change_control_surface.py`.

Verification reported by MainAgent:

- `python3 -m unittest tests.test_change_control_surface`: OK.
- `python3 -m unittest discover -s tests`: 124 tests OK.
- `git diff --check -- .codex tests layers SPEC.md E2E.md flake.nix flake.lock .github`: OK.

Observed issues:

- Direct `nix flake check --no-build` inside `AgentOrchestra/` failed because
  `AgentOrchestra/flake.nix` is untracked from the parent Git repository. This
  is the known local generated-fixture visibility limitation.
- `codex_apps` MCP startup timed out in one ProfessionalAgent pane, but the run
  did not rely on that MCP path and completed normally.

Impact:

- The accepted change closes a small PR/change-control gap for E2E evidence.
- No false-accept tmux delivery failure was observed in this run.

## 2026-05-25 01:29 JST - post-regeneration final E2E monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-012933-agent-orchestra`, after
regenerating `AgentOrchestra/` and reinstalling `codex-o`.

Result: PASS, but not a zero-problem E2E.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1167` / `pro-runtime`
  - `%1168` / `pro-qa`
- Initial tasks and peer consultation used the runtime tmux delivery helper.
- Both ProfessionalAgents reached `ready_for_review`, then `retired`.
- Final shared task file reached `[status] done`.
- ProfessionalAgent panes were still present after `/exit`, so MainAgent
  captured evidence and used `kill-pane`; final pane list showed only
  MainAgent pane `%967`.
- Verification reported by MainAgent:
  - `python3 -m py_compile .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py`: OK.
  - `git diff --check -- .codex tests layers SPEC.md E2E.md flake.nix flake.lock .github .gitignore`: OK.
  - `python3 -m unittest discover -s tests`: 124 tests OK.
  - `nix flake check --no-build --no-write-lock-file`: OK after the full
    flake check limitation was recorded.

Observed issues:

- MainAgent and `pro-runtime` both attempted `pytest` even though this project
  uses `unittest` and pytest is not installed.
- Full `nix flake check --no-write-lock-file` failed because root `E2E.md`
  was untracked, so Git-backed Nix source omitted it after the workflow/test
  contract started requiring it.

Accepted follow-up fixes:

- Make the standard verification runner explicit in SPEC and generated Agent
  templates: use `unittest`, `py_compile`, `git diff --check`, and Nix checks;
  do not run `pytest` unless explicitly requested or first confirmed available
  and necessary.
- Include root `E2E.md` in the Git index before the next final E2E so local
  Git-backed Nix source can see the evidence ledger that CI now requires.

## 2026-05-25 01:47 JST - pane-target normalization E2E monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-014756-agent-orchestra`.

Result: PASS, but not a zero-problem E2E because the run found and integrated
one additional improvement and had transient test failures while developing it.

Evidence:

- MainAgent pane `%967` launched one ProfessionalAgent:
  - `%1169` / `pro-runtime-qa`
- Initial task and follow-up review request used the runtime tmux delivery
  helper and were accepted.
- ProfessionalAgent reached `ready_for_review`, reviewed MainAgent's follow-up
  patch, accepted it, then was retired.
- Final shared task file reached `[status] done` with no open work and no
  unresolved candidates.
- ProfessionalAgent pane `%1169` was killed after accepted retirement; final
  pane cleanup succeeded.

Accepted change:

- Normalize blank or whitespace-only tmux pane ids before writing launch
  material env/state, so Hook wake targets remain deterministic and usable.
- Add regression coverage in `tests/test_launch_args.py`.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 126 tests OK after the patch.
- `python3 -m py_compile`: OK.
- `git diff --check -- AgentOrchestra`: OK.
- ProfessionalAgent review: accepted, no blocking objection.

Observed issues:

- The first targeted test run failed because the test read the generated state
  file after its temporary directory was already removed. MainAgent fixed the
  test and reran targeted tests successfully.
- Full unittest then failed on the 300-line file boundary after the first
  implementation shape. MainAgent moved the helper into `launch_args.py` and
  reran full unittest successfully.

Impact:

- The accepted change is valid and should be mirrored into the root source.
- Because transient test failures occurred, the improvement loop remains in
  progress until a later E2E completes without issues.

## 2026-05-25 02:05 JST - candidate-ledger contract E2E monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-020558-agent-orchestra`.

Result: PASS with one accepted improvement.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1170` / `pro-layer16-runtime`
  - `%1171` / `pro-layer04-quality`
- Initial tasks, peer consultation, and follow-up stop-edit messages used the
  runtime tmux delivery helper and were accepted.
- ProfessionalAgents reached `ready_for_review`, then `retired`.
- Final shared task file reached `[status] done` with all candidates
  dispositioned.
- ProfessionalAgent panes `%1170` and `%1171` remained after `/exit`, were
  captured, then killed; final cleanup succeeded.

Accepted change:

- Make candidate ledger finalization deterministic by rejecting duplicate
  candidate ids as invalid.
- Treat duplicate candidate field keys as unresolved instead of allowing later
  values to override earlier evidence.
- Document the uniqueness contract in `SPEC.md` and add regression tests.

Verification reported by MainAgent:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`: 128 tests OK.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile .codex/agent_orchestra_minimal/task_file.py`: OK.
- `git diff --check -- AgentOrchestra`: OK.
- Generated `__pycache__` / `*.pyc` artifacts were cleaned before final report.

Observed issues:

- No pytest attempt occurred.
- No E2E.md/Nix Git-source visibility issue occurred.
- No tmux false-accept was observed.
- A valid new improvement was found and integrated, so the loop continues.

Impact:

- This run was meaningfully more networked than previous ones: Pro-to-Pro
  questions and answers were observed.
- It still exposed the need for first-class protocol support. Without
  structured consultation/decision/change-unit records, network discussion
  remains ad hoc and easy to lose in tmux transcripts.
- No files were edited by the run; the result is a design recommendation ready
  for implementation.

## 2026-05-24 08:00 JST - final runtime-contract E2E monitoring

Scope: monitored the next `self-improvement` run in
`/private/tmp/agent-orchestra/20260524-072344-agent-orchestra` after the user
asked how to make the equal-editing/network model affect actual codex-o startup
behavior, not only SPEC.md.

Result: partially passed. The produced AgentOrchestra changes are largely
valuable and the AgentOrchestra test suite passes, but the run did not fully
complete its lifecycle protocol: Pro panes remained open and the shared task
file stayed at `[status] progress`.

Evidence:

- Main pane: `%967`.
- Active ProfessionalAgent panes at final observer check:
  - `%1146` / `pro-runtime-contract`
  - `%1147` / `pro-contract-qa`
- Both Pro state files were `ready_for_review`, not `retired`.
- `tasks.ini` still showed `[status] progress` with
  `inspect-runtime-surfaces` in `[InProgress]`.
- `tmux list-panes -t self-improvement` still showed `%967`, `%1146`, and
  `%1147`.
- MainAgent displayed `Goal achieved`, but did not retire the Pro panes or move
  the shared task file to done.

Observed changes proposed/implemented inside `AgentOrchestra/`:

- Runtime startup templates now encode the intended model:
  - `common.AGENTS.md`: AgentTeam steward, equal editing rights, Pro-to-Pro
    direct consultation, InReview not Main-only.
  - `main.AGENTS.md`: MainAgent as user-facing steward, not higher authority
    over ProfessionalAgents for editing/review/request-changes/blocking
    objections.
  - `professional.AGENTS.md`: ProfessionalAgents can edit, propose tasks,
    review peers, request changes, and raise blocking objections.
- Skills were aligned with runtime behavior:
  - `agent-orchestra-team`: equal-editing Team and Team/DRI integration
    readiness.
  - `agent-orchestra-tmux-common`: peer consultation evidence and direct
    Pro<->Pro collaboration.
  - `agent-orchestra-task-file`: `[InReview]` is peer/Team review, not
    Main-only waiting.
- SPEC.md was aligned with the same model.
- Contract tests were expanded:
  - launch material tests assert generated Main/Pro startup contains steward,
    no-outrank, change-unit DRI, Team review, and peer evidence language.
  - runtime-boundary tests assert behavior contract lives in templates/skills,
    not Python runtime logic.
  - skill/spec tests assert Team powers, consultation evidence, and InReview
    semantics.

Verification:

- MainAgent reported `python3 -m unittest discover -s tests` inside
  `AgentOrchestra/`: 101 tests OK.
- Observer reran the same command from
  `${AGENT_ORCHESTRA_LEGACY_ROOT}/AgentOrchestra`: 101 tests OK.

Important communication issue:

- The QA Pro sent a consultation request to runtime Pro `%1146`.
- The request became visible in the target pane but the target did not start
  processing it.
- The QA Pro detected this and sent an additional submit key with
  `tmux send-keys -t %1146 "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"`.
- Only after the extra submit did `%1146` begin working.
- A later QA-to-runtime message also required an explicit extra submit.

Assessment:

- The content direction is good and should be accepted: it targets the real
  startup surfaces that codex-o generates, not only SPEC.md.
- The implementation is still contract/documentation/test based. The next root
  improvement should make message delivery a first-class operation: send,
  verify target acceptance, retry submit if the composer still contains the
  message, and record failure as a communication defect.
- The lifecycle issue remains real: a MainAgent claiming goal completion while
  Pro panes are still `ready_for_review` and `tasks.ini` is still `progress` is
  a framework-level completion-gate bug, not a harmless exploration detail.

## 2026-05-24 09:24 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-091208-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS with important delivery-helper findings.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1148` / `pro-runtime`
  - `%1149` / `pro-security`
- Both ProfessionalAgents received tasks, reviewed each other directly, moved
  to `ready_for_review`, and were accepted by MainAgent.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final ProfessionalAgent states are `retired`.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane
  `%967`; `%1148` and `%1149` were killed after retirement cleanup.
- Candidate ledger was used and closed with five entries: four integrated
  fixes and one rejected/no-further-change sweep.

AgentOrchestra changes produced by the run:

- Generated launch env now includes isolated `CODEX_HOME` on `PYTHONPATH`, so
  `python -m agent_orchestra_minimal.tmux_send` works from launched Agent
  panes.
- `tmux_send.py` supports direct script execution, blank submit-key defaulting,
  and stronger wrapped-composer retry detection.
- `send_wake` defaults blank submit keys to `C-m` consistently with launch and
  Stop Hook behavior.
- Stop Hook target selection now prefers launch-provided
  `AGENT_ORCHESTRA_TMUX_PANE` / `TMUX_PANE` over mutable `state.json`
  `tmux_target`; state remains fallback only when env has no pane.
- Regression tests were added or updated in `test_launch_material_io.py`,
  `test_tmux_send.py`, and `test_stop_hook_and_tmux.py`.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 102 tests OK.
- `py_compile` over `.codex/agent_orchestra_minimal`, `.codex/hooks`, and
  `tests`: OK.
- `git diff --check -- AgentOrchestra`: OK.
- Shared task parser confirmed final status `done` with no open work.

Observed issues:

- Initial helper usage failed with `ModuleNotFoundError` because the isolated
  env did not set `PYTHONPATH=$CODEX_HOME`.
- Direct script execution of `tmux_send.py` failed because the module used a
  relative import without script-mode compatibility.
- The first `tmux_send` acceptance check falsely reported success for a long
  wrapped composer message; the message stayed visible and Pro agents did not
  start until MainAgent sent an extra `C-m`.
- Later, pro-security to pro-runtime review delivery required two submit
  attempts and reported `accepted after 2 submit attempt(s)`, showing the retry
  path is exercised in live TUI use.
- `/exit` retirement still did not remove all panes quickly. MainAgent observed
  `%1148` as `zsh` and `%1149` as `node`, then used `tmux kill-pane`; final
  cleanup succeeded.

Assessment:

- This run directly reproduced the user's pane-delivery concern and produced
  targeted fixes in `AgentOrchestra/`.
- The proposed fixes are root-cause oriented: package import path, script-mode
  compatibility, submit-key normalization, wrapped composer acceptance
  detection, and trusted pane-target precedence.
- The remaining retirement behavior is acceptable as a cleanup fallback, but
  graceful `/exit` is still not guaranteed to remove every pane promptly.

## 2026-05-24 09:48 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-093458-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS, but initial ProfessionalAgent delivery still required manual
extra submit by MainAgent.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1150` / `pro-runtime-16`
  - `%1151` / `pro-qa-15`
- Initial tasks were sent with `tmux_send`, and MainAgent saw
  `accepted after 1 submit attempt(s)` for both panes.
- Both Pro panes stayed idle with the task visible for more than a minute.
- MainAgent detected the non-starting panes and sent plain `C-m` to both; only
  after that did the ProfessionalAgents start working.
- After the extra submit, direct Pro-to-Pro review worked:
  - pro-qa requested changes from pro-runtime on a line-limit regression.
  - pro-runtime addressed the request by splitting tests and rerunning checks.
  - pro-qa independently re-reviewed and accepted.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final ProfessionalAgent states are `retired`.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane
  `%967`; `%1150` and `%1151` were removed by `tmux kill-pane`.

AgentOrchestra changes produced by the run:

- Added shared `tmux_delivery.py` so normal `tmux_send` messages and Stop Hook
  wake delivery use the same paste -> submit -> capture -> retry path.
- Refactored `tmux_send.py` to delegate to shared delivery code.
- Refactored `tmux_wake.py` so `send_wake` returns delivery evidence and
  `run_stop_hook` records `_wake_delivery_unaccepted` when wake payload remains
  in the composer through retries.
- Routed invalid task-file wake and invalid agent-state main fallback wake
  through the same delivery-result path.
- Added delivery-failure regression coverage in
  `tests/test_stop_hook_delivery_failure.py`.
- Updated runtime/source-contract allowlists for `tmux_delivery.py`.
- Strengthened PR checklist and tests so change-unit metadata and completed
  `[Candidates]` dispositions are required merge evidence.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 105 tests OK.
- `py_compile` over `.codex/agent_orchestra_minimal`, `.codex/hooks`, and
  `tests`: OK.
- `git diff --check -- .codex tests SPEC.md flake.nix flake.lock .github Handoff.md`: OK.
- Temporary copied fixture `nix flake check --no-build`: OK.
- Temporary copied fixture `nix build .#checks.aarch64-darwin.source-contract --no-link`: OK.
- Direct `nix flake check --no-build` inside `AgentOrchestra/` failed because
  `AgentOrchestra/flake.nix` is untracked from the parent Git repo.

Observed issues:

- The core delivery problem still reproduced at run start: helper acceptance
  did not mean the target Agent began processing.
- This is not a `C-m` normalization issue. The submit key was already `C-m`;
  the failure is the acceptance/verification contract.
- The current Skill intent is correct: delivery is complete only after the
  target Codex TUI accepts the message, not after text is pasted. The helper
  implementation still did not prove that at launch-time.
- MainAgent manually compensated by sending `C-m`, and later implemented a
  stronger shared delivery path. That proposal is relevant, but it still needs
  root-side review before assuming the live delivery issue is fully solved.

Assessment:

- Accept the runtime delivery proposal in principle. It is a root-cause
  direction because it centralizes delivery verification and makes Hook wake
  delivery failures observable.
- Accept the QA/change-control proposal. It strengthens evidence requirements
  without constraining exploratory development.
- Do not treat this E2E as proof that task delivery is fixed. It proves the
  previous implementation still failed, and that AgentOrchestra produced the
  next candidate fix.

## 2026-05-24 10:00 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-100022-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS, but tmux/Codex TUI delivery acceptance is still not reliable.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1152` / `pro-runtime-16`
  - `%1153` / `pro-sre-22`
- Initial task delivery reported `accepted after 1 submit attempt(s)` for both
  ProfessionalAgents.
- `pro-runtime-16` began work immediately.
- `pro-sre-22` did not begin work after the initial accepted delivery. The
  task remained visible in the composer for more than a minute.
- MainAgent sent an extra `C-m` to `%1153`, but the pane still did not start
  immediately. It began after a later peer-check message from `pro-runtime-16`
  was sent, effectively submitting the already queued text together with the
  peer message.
- A later final review request again reported `accepted after 1 submit
  attempt(s)` for both Pro panes, but MainAgent waited 30 seconds and then sent
  explicit `C-m` to both panes.
- Despite the delivery issue, both ProfessionalAgents completed reviews.
- `pro-sre-22` found and fixed a real candidate-ledger parser bug during final
  review.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Final ProfessionalAgent states are `retired`.
- MainAgent verified and then killed lingering Pro panes. Final
  `tmux list-panes -t self-improvement` showed only MainAgent pane `%967`.

AgentOrchestra changes produced by the run:

- Stop Hook wake delivery exceptions now return typed
  `_wake_delivery_failed` decisions instead of collapsing into a generic hook
  exception.
- Completed candidate ledger entries now require candidate id, disposition,
  summary, and evidence.
- Candidate evidence values may contain colons, covering `tests/file.py:12`,
  URLs, and `pane:%1153`.
- Launch material regeneration always cleans isolated `workspace`, `home`, and
  `codex_home`.
- Launch material rejects ancestor `AGENTS.md` contamination outside the
  generated isolated workspace.
- tmux delivery stuck-composer detection scans all captured lines instead of
  only the tail window, improving long wrapped prompt detection.
- The source-contract workflow now uses `permissions: contents: read` and pins
  third-party actions by commit SHA.
- Added/updated tests, including `test_candidate_ledger_contract.py` and
  `test_launch_cleanup_contract.py`.
- Updated `Handoff.md` to 111 tests.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 111 tests OK.
- `python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py')`: OK.
- `git diff --check -- .codex tests Handoff.md SPEC.md flake.nix flake.lock .github`: OK.
- Temporary copied fixture `nix flake check --no-build`: OK.
- Temporary copied fixture `nix build .#checks.aarch64-darwin.source-contract --no-link`: OK.
- Direct `nix flake check --no-build` inside `AgentOrchestra/` failed because
  `AgentOrchestra/flake.nix` is untracked from the parent Git repo.

Observed issues:

- Delivery acceptance is still not a reliable proof that the target Agent has
  started processing.
- The issue is not just submit-key normalization. The runtime used `C-m`, and
  MainAgent still had to use manual extra submits.
- MainAgent correctly detected the stuck review request and compensated, but
  this is still a core communication reliability defect.
- The new long-composer detection is a good improvement, but this run did not
  prove full delivery responsibility is fixed.

Assessment:

- Accept most produced changes as relevant and root-cause oriented.
- Treat the workflow SHA pinning as a separate supply-chain hardening change;
  it is valid but less central than the orchestration/runtime fixes.
- The highest priority remaining issue is still reliable send completion:
  accepted delivery must mean the target Codex TUI has actually started
  processing, or the helper must return failure and force retry/escalation.

## 2026-05-24 20:03 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-200326-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS, with a clear initial tmux delivery false-accept recurrence that
AgentOrchestra identified and patched during the run.

Evidence:

- MainAgent pane `%967` launched two ProfessionalAgents:
  - `%1154` / `pro-runtime`
  - `%1155` / `pro-qa-release`
- MainAgent sent initial investigation tasks to both ProfessionalAgents.
- Both task messages remained visible in the Codex composer and neither
  ProfessionalAgent began processing until MainAgent manually submitted extra
  `${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}`.
- This reproduced the core communication issue: the runtime treated delivery as
  successful or did not enforce the helper contract, while visible queued text
  remained in the target pane.
- MainAgent recognized this explicitly and described the problem as stale
  activity markers being counted as accepted delivery while the actual message
  remained queued.
- After manual submit, both ProfessionalAgents worked and reviewed the fix:
  - `pro-runtime` accepted, with focused 31 tests OK and full 114 tests OK.
  - `pro-qa-release` accepted, with focused 32 tests OK and full 114 tests OK.
- A review request to `pro-runtime` also remained in the composer until
  MainAgent sent another explicit submit. This further supports the same
  delivery-reliability diagnosis.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Candidate ledger was fully dispositioned.
- Final ProfessionalAgent states are `retired`.
- Final `tmux list-panes -t self-improvement` showed only MainAgent pane `%967`;
  `%1154` and `%1155` were cleaned up.

AgentOrchestra changes produced by the run:

- `AgentOrchestra/.codex/agent_orchestra_minimal/tmux_delivery.py`
  changed delivery-state detection so, when a message probe is still visible,
  stale activity markers before the last visible probe do not count as
  successful delivery.
- Added regression coverage in
  `AgentOrchestra/tests/test_tmux_send.py` for stale activity before a
  still-visible message.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 114 tests OK.
- Focused `tests.test_tmux_send`: 11 tests OK.
- Runtime review focused checks:
  `tests.test_tmux_send tests.test_stop_hook_and_tmux tests.test_submit_key_defaults`:
  31 tests OK.
- QA review focused checks:
  `tests.test_tmux_send tests.test_stop_hook_delivery_failure tests.test_stop_hook_and_tmux`:
  32 tests OK.

Candidate dispositions:

- Integrated: tmux delivery must not accept stale activity before a
  still-visible message probe.
- Rejected: require pytest as a runner; the project standard unittest path
  passed.
- Rejected: split runtime code for line limits; runtime files were below the
  hard limit.
- Rejected: additional task-file/candidate-ledger patch; existing coverage was
  judged sufficient.
- Rejected: additional SubAgent spawn for final review; ProfessionalAgents
  provided peer review evidence.

Observed issues:

- Initial delivery still failed in live Codex TUI interaction.
- A later review delivery also required manual submit.
- This proves the earlier accepted-delivery contract remained insufficient in
  the live environment at the start of this run.

Assessment:

- Accept the produced fix. It is directly tied to the observed failure mode and
  tightens the delivery acceptance predicate without adding semantic control.
- This run is not proof that live delivery is fully fixed, because the patch was
  created after the failed deliveries. The next E2E run is needed to verify that
  initial tasks and later review requests no longer require manual extra submit.

## 2026-05-24 22:33 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260524-223357-agent-orchestra`.
No target fixes were applied by this observer.

Result: PASS, with two further delivery-contract issues observed and patched
during the run.

Manual evidence procedure exercised:

1. MainAgent started with `codex-o` for this target project.
2. MainAgent wrote `[status] progress` before substantial investigation.
3. MainAgent created two ProfessionalAgent tmux panes.
4. MainAgent prepared both ProfessionalAgents with `prepare_agent_launch.py`
   and layer `INSTRUCTIONS.md` specialist perspectives.
5. MainAgent launched each pane from generated `env.sh` and `command.json`.
6. MainAgent sent initial tasks and review requests with the runtime tmux
   delivery helper.
7. ProfessionalAgents sent peer-consultation messages with the same helper.
8. Agents captured panes and recorded sender, receiver, topic, helper result,
   response, and disposition as review evidence.
9. ProfessionalAgents wrote `ready_for_review` before final acceptance.
10. MainAgent retired accepted ProfessionalAgents with `/exit`, verified pane
    cleanup, and used `tmux kill-pane` only after accepted retirement.

Evidence:

- MainAgent pane `%967` launched:
  - `%1159` / `pro-runtime`
  - `%1160` / `pro-qa`
- Initial task delivery to both ProfessionalAgents used
  `agent_orchestra_minimal.tmux_send` and was accepted after retries.
- `pro-runtime` and `pro-qa` exchanged peer-consultation messages with the
  helper.
- One later `pro-runtime` to `pro-qa` send while `pro-qa` was working returned
  not accepted; the Agent recorded this as delivery failure instead of treating
  the message as delivered.
- MainAgent observed that helper acceptance could still be fooled when a
  prompt/composer marker remained but the submitted-message probe was absent.
- MainAgent patched `tmux_delivery.py` so stale activity before the last prompt
  marker no longer proves acceptance, and added regression coverage.
- MainAgent added a repeatable live tmux E2E evidence procedure and contract
  coverage so this evidence path is not purely tribal knowledge.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Candidate ledger dispositions were complete:
  - integrated: recursive Python 300-line hard limit contract;
  - integrated: tmux delivery prompt-marker false-accept fix;
  - integrated: live tmux E2E evidence procedure;
  - deferred: fully automated live Codex TUI E2E, because it requires
    interactive tmux/Codex panes.
- Final ProfessionalAgent states were `retired`.
- Final pane list no longer contained `%1159` or `%1160`.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests -q`: 119 tests OK.
- `python3 -m py_compile .codex/agent_orchestra_minimal/tmux_delivery.py`: OK.
- File line check after changes:
  `tmux_delivery.py` 128 lines, `test_tmux_send.py` 237 lines,
  `test_spec_contract.py` 190 lines.

Observed issues:

- `nix develop --command python3 -m unittest discover -s tests` inside
  untracked `AgentOrchestra/` failed because Nix could not see
  `AgentOrchestra/flake.nix` from the parent Git repository.
- Fully automated live Codex TUI E2E remains opt-in because it depends on a
  running tmux session and interactive Codex panes.

Assessment:

- Accept the tmux delivery prompt-marker fix, but integrate it into root with
  a refined predicate: if the submitted-message probe is absent but a prompt
  marker remains, only activity after the last prompt marker can prove
  acceptance.
- Preserve this root `E2E.md` as the live evidence ledger rather than creating
  a separate generated-copy source of truth.

## 2026-05-25 00:11 JST - self-improvement monitoring

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-001154-agent-orchestra`.
No target fixes were applied by this observer during the run.

Result: PASS, with initial delivery false negatives but no false-accept.

Evidence:

- MainAgent pane `%967` launched:
  - `%1161` / `pro-runtime-16`
  - `%1162` / `pro-spec-04`
- Initial task delivery through the runtime tmux helper returned not accepted
  for both ProfessionalAgents. MainAgent did not treat those sends as
  successful; it recorded delivery failure and recovered with an explicit extra
  submit.
- Both ProfessionalAgents started, reviewed the generated-copy changes, and
  reached `ready_for_review` with no blocking objection.
- MainAgent integrated a `--polls-per-attempt` helper improvement in the
  generated copy so slow Codex TUI startup can be observed before a retry
  sends another submit.
- Follow-up review sends using the improved helper were accepted after one or
  two submit attempts.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Candidate ledger dispositions were complete:
  - integrated: tmux delivery helper polls after submit before retry;
  - integrated: tmux common Skill documents `--polls-per-attempt`;
  - integrated: SPEC candidate ledger re-kick condition includes missing id,
    summary, or evidence pointer;
  - integrated: SPEC hard 300 line code limit measured by contract test;
  - deferred: broader live Codex TUI end-to-end delivery reliability remains
    opt-in operational evidence.
- ProfessionalAgent panes `%1161` and `%1162` were retired and cleaned up.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 121 tests OK.
- `python3 -m py_compile ...`: OK.
- `git diff --check -- .`: OK.
- ProfessionalAgent peer review: no blocking objection.

Assessment:

- Accept the run as proof that the false-accept path is closed for this
  scenario: helper failure was explicit and MainAgent did not continue as if
  delivery had succeeded.
- Accept `--polls-per-attempt` as a liveness improvement, but move it into root
  deliberately rather than treating generated `AgentOrchestra/` as the source.
- Do not duplicate the hard line-limit contract in `test_spec_contract.py`;
  strengthen the existing runtime boundary line-limit test instead.

## 2026-05-25 01:15 JST - ProfessionalAgent state recovery contract

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-005445-agent-orchestra`.

Result: PASS with delivery false-negative observations and expected Nix
visibility limitation.

Evidence:

- MainAgent pane `%967` launched:
  - `%1163` / `pro-runtime`
  - `%1164` / `pro-qa`
- Both ProfessionalAgents reviewed `SPEC.md` against generated
  `AgentOrchestra/` and reached `ready_for_review` with no blocking objection.
- Integrated generated-copy changes:
  - `tmux_wake.py` preserves liveness when a stopped ProfessionalAgent has a
    deterministic pane and `AGENT_ORCHESTRA_AGENT_KIND=ProfessionalAgent`, but
    its state file is missing, unreadable, or invalid.
  - The ProfessionalAgent kind comparison strips whitespace and lowercases
    before recovery matching.
  - Stop Hook recovery tests cover missing/invalid ProfessionalAgent state with
    deterministic pane, plus the no-pane quiet case.
  - Change-control tests fix CI path gate coverage for hooks, Skills, flake
    files, and the workflow file itself.
- Final shared task file reached `[status] done` with empty Backlog,
  InProgress, and InReview sections.
- Candidate ledger dispositions were complete:
  - integrated: ProfessionalAgent missing/invalid state fixed-wake liveness and
    kind normalization;
  - integrated: CI source-contract path coverage for Hook, Skill, flake, and
    workflow surfaces;
  - integrated: runtime evidence ledger update;
  - deferred: Nix source-contract verification until `AgentOrchestra/` is
    tracked or otherwise visible to Nix as a clean source.
- ProfessionalAgent states were `retired`, and panes `%1163` / `%1164` were
  cleaned up with the documented kill-pane fallback after `/exit` left them
  present.

Verification reported by MainAgent:

- `python3 -m unittest discover -s tests`: 123 tests OK.
- `python3 -m py_compile ...`: OK.
- `git diff --check -- .codex tests E2E.md`: OK.
- ProfessionalAgent peer review: no blocking objection.

Observed issues:

- Runtime helper delivery to a peer/review pane sometimes returned not accepted
  while the target pane was still finishing current work. Agents treated this
  as explicit delivery failure and recovered with an extra submit, so this was
  not a false-accept.
- `pytest` was attempted even though this project uses `unittest` and pytest is
  not installed.
- Direct Nix checks inside untracked `AgentOrchestra/` still failed because Nix
  could not materialize `AgentOrchestra/flake.nix` from the parent Git source.

Assessment:

- Accept the generated-copy state-recovery and change-control test changes.
- Keep the local loop status as `progress`, because the E2E still observed a
  delivery false-negative.
- Address the delivery false-negative in root by extending the bounded helper
  confirmation window for peer panes that are still completing their current
  turn.

## 2026-05-25 02:23 JST - poll bounds, launch cleanup, and false-accept recurrence

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-022347-agent-orchestra`.

Result: PASS with accepted improvements, plus one helper false-accept
recurrence that required external recovery.

Evidence:

- MainAgent pane `%967` launched `pro-runtime-review` in pane `%1172`.
- Initial ProfessionalAgent task delivery used the runtime helper and was
  accepted after two submit attempts.
- MainAgent accepted and implemented a bounded delivery-helper improvement:
  `poll_interval_seconds < 0` is now rejected.
- ProfessionalAgent accepted and implemented a bounded launch-material cleanup
  improvement: stale symlinks/files at isolated workspace, home, or
  `codex_home` paths are unlinked before regeneration, while real directories
  are removed recursively.
- Full generated-copy verification recovered to green:
  `python3 -m unittest discover -s tests`: 129 tests OK.
- `nix flake check --no-build` from inside the untracked generated copy failed
  because parent Git cannot materialize `AgentOrchestra/flake.nix`; the
  equivalent `path:${AGENT_ORCHESTRA_LEGACY_ROOT}/AgentOrchestra`
  evaluation passed.
- MainAgent closed the shared task file with `[status] done`, no open work, and
  no unresolved candidates. ProfessionalAgent pane cleanup completed after the
  documented kill-pane fallback.

Observed issues:

- MainAgent sent a follow-up review request to `%1172`; the helper reported
  `accepted after 1 submit attempt(s)`, but the message remained visible in the
  ProfessionalAgent composer with `tab to queue message`. An external extra
  `C-m` was required to continue. This is a true tmux delivery false-accept.
- The generated-copy full suite initially failed twice because new tests pushed
  files over the hard 300-line boundary. The AgentTeam compressed the tests and
  recovered.
- The normal-form Nix check remains noisy for the generated-copy/untracked
  policy, though `path:` evaluation works.

Assessment:

- Accept both generated-copy improvements and move them into root.
- Treat the helper false-accept as a blocking loop issue. Root now prioritizes
  visible queued/composer hints over stale start markers when judging delivery.
- Keep the local loop status as `progress`; a clean E2E has not been observed
  after this fix.

## 2026-05-25 02:51 JST - clean delivery plus accepted contract improvements

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-024053-agent-orchestra`.

Result: PASS with no observed E2E delivery or orchestration failures, but with
accepted improvement proposals that require a follow-up implementation cycle.

Evidence:

- MainAgent pane `%967` launched `pro-runtime-16` in pane `%1173` and
  `pro-docs-25` in pane `%1174`.
- Initial ProfessionalAgent task delivery used the runtime tmux helper for both
  panes and was accepted after two submit attempts. The messages entered the
  conversation and both agents began work; no false-accept recurrence was
  observed.
- ProfessionalAgent peer consultation and MainAgent ready-for-review follow-up
  messages also used the runtime helper. Delivery was confirmed and no queued
  composer message required external recovery.
- `pro-runtime-16` proposed and implemented deterministic candidate ledger
  field-key normalization: required candidate fields are case-insensitive and
  duplicate keys are detected case-insensitively.
- `pro-docs-25` proposed and implemented SPEC Operating Identity alignment for
  generated startup metadata, helper-based delivery, ProfessionalAgent
  consultation evidence, Candidates semantics, and InReview semantics.
- MainAgent verification in the generated copy reported
  `python3 -m unittest discover -s tests`: 131 tests OK, `py_compile`: OK, and
  whitespace checks OK.
- MainAgent closed `tasks.ini` with `[status] done`, no Backlog/InProgress/
  InReview items, integrated/rejected Candidates only, and retired panes
  `%1173` / `%1174` with cleanup confirmed.

Observed issues:

- None in live tmux delivery or AgentOrchestra orchestration.

Assessment:

- Accept the two integrated improvement proposals and move them into root.
- Keep the local loop status as `progress` until the accepted changes are
  verified, `codex-o` is reinstalled, `AgentOrchestra/` is regenerated, and one
  final E2E confirms that no new issue was introduced.

## 2026-05-25 03:08 JST - runtime file-size and pane-detection contract proposals

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-025516-agent-orchestra`.

Result: PASS with accepted improvement proposals; no live delivery failure
required external recovery.

Evidence:

- MainAgent pane `%967` launched `pro-runtime-review` in pane `%1175`.
- ProfessionalAgent initial task delivery used the runtime tmux helper and was
  reported accepted after two submit attempts. The pane subsequently entered
  the requested task without any external submit recovery.
- MainAgent added a runtime file-size contract test enforcing the SPEC.md
  300-line hard limit for `.codex/agent_orchestra_minimal` and `.codex/hooks`
  Python files.
- ProfessionalAgent removed the bare `tmux display-message` fallback from
  `current_tmux_pane()` and added a regression test proving active-client panes
  are not inferred as the current Agent pane.
- Generated-copy verification reported `python3 -m unittest discover -s tests`:
  133 tests OK, runtime `py_compile`: OK, `git diff --check`: OK,
  `nix flake check --no-build path:${AGENT_ORCHESTRA_LEGACY_ROOT}/AgentOrchestra`:
  OK, and `nix build path:${AGENT_ORCHESTRA_LEGACY_ROOT}/AgentOrchestra#checks.aarch64-darwin.source-contract`:
  OK.
- The normal-form Nix check inside the generated copy still failed because
  `AgentOrchestra/` is intentionally untracked from the parent Git tree; the
  path-form check is the valid generated-copy verification.
- MainAgent closed the generated-copy task file with `[status] done`, no open
  Backlog/InProgress/InReview items, two integrated Candidates, two rejected
  Candidates with evidence, and retired pane `%1175`.

Observed issues:

- None in live tmux delivery or AgentOrchestra orchestration.
- Accepted proposals remain, so this is not a terminal clean loop iteration.

Assessment:

- Accept both integrated proposals and move them into root.
- Keep the local loop status as `progress` until root verification,
  `codex-o` reinstall, generated-copy regeneration, and another final E2E run
  complete with no issues and no accepted follow-up improvements.

## 2026-05-25 03:26 JST - candidate ids and queued-marker false-positive hardening

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-031152-agent-orchestra`.

Result: PASS with accepted improvement proposals; no live delivery failure
required external recovery.

Evidence:

- MainAgent pane `%967` launched `pro-runtime` in pane `%1176` and
  `pro-spec-qa` in pane `%1177`.
- Initial ProfessionalAgent task delivery used the runtime tmux helper for both
  panes and both agents entered Working state. No additional external submit was
  needed after helper acceptance.
- MainAgent and ProfessionalAgents integrated three improvements:
  candidate IDs are casefold-normalized for duplicate detection; tmux delivery
  start markers are accepted only as non-indented line starts; and FakeTmuxSend
  was split into `tests/tmux_send_helpers.py` so `tests/test_tmux_send.py`
  remains below the 300-line limit while keeping the queued-marker regression.
- Full generated-copy verification reported `python3 -m unittest discover -s
  tests`: 135 tests OK, Python compile OK, and `git diff --check`: OK.
- Both ProfessionalAgents accepted the final change set with no blocking
  objections. MainAgent closed `tasks.ini` with `[status] done`, completed
  Candidates only, and retired/cleaned panes `%1176` and `%1177`.

Observed issues:

- None in live tmux delivery or orchestration.
- Accepted proposals remain, so this iteration still requires root
  implementation and a follow-up E2E.

Assessment:

- Accept the integrated improvements and move them into root.
- Keep the local loop status as `progress` until root verification,
  `codex-o` reinstall, generated-copy regeneration, and another E2E run finish
  with zero issues and no accepted proposals.

## 2026-05-25 03:42 JST - PR evidence rails and stricter prompt-history delivery

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-033014-agent-orchestra`.

Result: PASS with accepted improvement proposals; no live delivery failure
required external recovery.

Evidence:

- MainAgent pane `%967` launched `pro-runtime` in pane `%1178` and `pro-qa`
  in pane `%1179`.
- Initial task delivery to both ProfessionalAgents used the runtime tmux helper
  and both agents began work.
- QA integrated PR-template evidence rails requiring direct `py_compile` and
  `git diff --check` evidence for runtime/instruction changes, plus
  `test_change_control_surface.py` coverage.
- Runtime integrated stricter tmux delivery behavior: unrelated prompt-history
  activity without current-message evidence remains `uncertain` instead of
  becoming delivery success.
- Generated-copy verification passed: full unittest 135 tests OK,
  `py_compile` OK, `git diff --check` OK, path-form Nix flake evaluation OK,
  and source-contract build OK.
- MainAgent closed `tasks.ini` with `[status] done`, no open work, integrated
  Candidates for the two changes, and retired/cleaned panes `%1178` and `%1179`.

Observed issues:

- None in live tmux delivery or orchestration.
- Accepted proposals remain, so a root implementation and follow-up E2E are
  required.

Assessment:

- Accept the integrated improvements and move them into root.
- Keep the local loop status as `progress` until the follow-up E2E has no
  issues and no accepted proposals.

## 2026-05-25 04:00 JST - delivery bounds and generated-copy spec drift

Scope: monitored tmux session `self-improvement` for run
`/private/tmp/agent-orchestra/20260525-034542-agent-orchestra`.

Result: PASS with accepted improvement proposals; no live delivery failure
required external recovery.

Evidence:

- MainAgent pane `%967` launched `pro-runtime-16` in pane `%1180` and
  `pro-docs-25` in pane `%1181`.
- Initial ProfessionalAgent task delivery used the runtime tmux helper for both
  panes and both agents entered work without external recovery.
- Docs/spec integrated a generated-copy SPEC drift fix: ProfessionalAgents are
  described as starting from their layer perspective rather than
  layer-specific instructions, with a negative regression assertion in
  `tests/test_spec_contract.py`.
- Docs/spec also refreshed `Handoff.md` verification wording from the stale
  113-test baseline to the current 135-test generated-copy evidence.
- Runtime integrated bounded delivery polling parameters for the tmux helper:
  `max_retries`, `poll_interval_seconds`, and `polls_per_attempt` now have
  upper bounds, with regression coverage in `tests/test_tmux_send.py`.
- MainAgent verification passed: full unittest 135 tests OK, touched Python
  and tests `py_compile` OK, `git diff --check` OK, and trailing whitespace
  sweep clean.
- MainAgent closed `tasks.ini` with `[status] done`, integrated Candidates for
  the accepted changes, and reported no unresolved candidates.

Observed issues:

- None in live tmux delivery or orchestration.
- Accepted proposals remain, so a root implementation and follow-up E2E are
  required.

Assessment:

- Accept the integrated improvements and move them into root.
- Keep the local loop status as `progress` until root verification,
  `codex-o` reinstall, generated-copy regeneration, and a follow-up E2E finish
  with no live issues and no accepted proposals.

## 2026-05-25 04:15 JST - ProfessionalAgent handoff and completion gates

Scope: monitored tmux session `72` for run
`/private/tmp/agent-orchestra/20260525-040139-agent-orchestra`.

Result: PASS with accepted improvement proposals and live issues that required
follow-up hardening.

Evidence:

- MainAgent pane `%1182` launched ProfessionalAgent panes `%1183` and `%1184`.
- Initial `prepare_agent_launch.py` calls failed because `--instruction-source`
  was passed as a single-quoted `$AGENT_ORCHESTRA_TARGET_PROJECT/...` path,
  preventing shell expansion. Main recovered by rerunning with absolute paths.
- After recovery, ProfessionalAgent task delivery used the runtime tmux helper
  and both ProfessionalAgents began work.
- Accepted improvements:
  - SPEC Completion Criteria now includes current runtime gates: delivery
    helper false-accept prevention, consultation evidence, completed
    `[Candidates]`, retired ProfessionalAgent pane cleanup, and path-form Nix
    checks for generated-copy verification.
  - ProfessionalAgent startup contract now requires moving or recording scoped
    work as awaiting review in the shared task file, and only moving it to Done
    once an accepted disposition is known.
  - Generated `__pycache__` / `.pyc` artifacts were removed from the generated
    copy.
- Full generated-copy verification passed after an intermediate line-limit
  failure was fixed: `python3 -m unittest discover -s tests` 136 tests OK,
  `py_compile` OK, `git diff --check` OK, path-form `nix flake check` OK, and
  source-contract build OK.
- MainAgent closed `tasks.ini` with `[status] done`, completed Candidates only,
  retired both ProfessionalAgents, and cleaned up panes `%1183` and `%1184`.

Observed issues:

- `prepare_agent_launch.py` was first invoked with a single-quoted environment
  variable path, causing a literal `$AGENT_ORCHESTRA_TARGET_PROJECT` lookup and
  manual recovery.
- A generated contract-test edit briefly pushed
  `tests/test_launch_material_contract.py` over the 300-line hard limit before
  being compressed back under the limit.
- Accepted proposals remain, so a root implementation and follow-up E2E are
  required.

Assessment:

- Accept the integrated improvements and move them into root.
- Add launch-skill contract coverage preventing single-quoted
  `$AGENT_ORCHESTRA_TARGET_PROJECT` paths in `prepare_agent_launch.py` examples.
- Keep the local loop status as `progress` until root verification,
  `codex-o` reinstall, generated-copy regeneration, and a follow-up E2E finish
  with no live issues and no accepted proposals.

## 2026-05-25 04:35 JST - AgentState identity and generated-copy Nix evidence

Scope: monitored tmux session `72` for run
`/private/tmp/agent-orchestra/20260525-041735-agent-orchestra`.

Result: PASS with accepted improvement proposals; no live delivery failure
required external recovery.

Evidence:

- MainAgent pane `%1185` launched ProfessionalAgent panes `%1186` and `%1187`.
- The previous single-quoted `--instruction-source` failure did not recur;
  launch used expanded target-project paths.
- Initial task delivery to both ProfessionalAgents used the runtime tmux helper.
  Runtime was accepted after one submit attempt and QA after two submit
  attempts, without an external extra submit.
- Accepted improvements:
  - `AgentState` now normalizes `agent_kind` in `__post_init__`, accepts
    documented MainAgent/ProfessionalAgent aliases, and rejects unknown values
    so Stop Hook identity cannot silently collapse to the wrong class.
  - Agent state contract tests were split into `tests/test_agent_state_contract.py`
    after an intermediate full-test failure exposed the 300-line hard limit in
    `tests/test_minimal_runtime_core.py`.
  - The PR checklist and `test_change_control_surface.py` now require
    path-form Nix checks for generated-copy or untracked-fixture verification.
  - `test_runtime_boundaries.py` now pins the required consultation evidence
    fields documented in the tmux common skill.
- Generated-copy verification passed: full unittest 142 tests OK, touched
  Python `py_compile` OK, `git diff --check -- AgentOrchestra` OK,
  path-form `nix flake check --no-build` OK, and path-form source-contract
  build OK.
- MainAgent closed `tasks.ini` with `[status] done`, no open work, no unresolved
  candidates, retired both ProfessionalAgents, and cleaned up panes `%1186` and
  `%1187`.

Observed issues:

- No live tmux delivery or orchestration issue remained in this run.
- Accepted proposals remain, so a root implementation and follow-up E2E are
  required.

Assessment:

- Accept the integrated improvements and move them into root.
- Keep the local loop status as `progress` until root verification,
  `codex-o` reinstall, generated-copy regeneration, and a follow-up E2E finish
  with no live issues and no accepted proposals.

## 2026-05-25 04:50 JST - task-file baseline contract and Stop Hook fallback

Scope: monitored tmux session `72` for run
`/private/tmp/agent-orchestra/20260525-043728-agent-orchestra`.

Result: PASS with accepted improvement proposals; no external recovery was
needed, but one consultation helper send returned non-accepted while the target
pane was busy and was handled explicitly.

Evidence:

- MainAgent pane `%1188` launched `pro-runtime-16-current` in `%1189` and
  `pro-doc-25-current` in `%1190`.
- Initial task delivery used the runtime helper and both ProfessionalAgents
  entered work. Runtime accepted after two submit attempts; docs accepted after
  two submit attempts.
- Accepted improvements:
  - Stop Hook recovery now wakes `AGENT_ORCHESTRA_MAIN_TMUX_PANE` when an
    active ProfessionalAgent has no deterministic own pane target and the
    shared task file is missing, unreadable, or invalid. Regression coverage was
    added to `tests/test_stop_hook_recovery.py`.
  - SPEC, common Agent guidance, and task-file Skill now distinguish the quiet
    initialized empty task file (`[status] done`) from active/discovery work,
    which must record open work and switch to `[status] progress`.
- Generated-copy verification passed after intermediate failures were fixed:
  full unittest 145 tests OK, `py_compile` OK, `git diff --check` OK,
  path-form `nix flake check --no-build` OK, and path-form source-contract
  build OK.
- MainAgent closed `tasks.ini` with `[status] done`, integrated the accepted
  candidates, rejected broader DEFAULT_TASK_FILE behavior changes, retired both
  ProfessionalAgents, and cleaned up panes `%1189` and `%1190`.

Observed issues:

- A MainAgent-to-runtime consultation helper attempt reported
  "message was not accepted by target Codex TUI after retries" while the runtime
  pane was busy. Main did not silently continue as if that send succeeded; peer
  evidence was later delivered and reviewed through accepted helper sends.
- Targeted/full tests briefly failed because of fixture setup, line-limit
  placement, and SPEC wording assertion drift. Agents fixed these during the run.
- Accepted proposals remain, so root implementation and another follow-up E2E
  are required.

Assessment:

- Accept both integrated improvements and move them into root.
- Treat the non-accepted consultation helper send as observed but not a new
  helper false-accept defect: the helper returned non-zero, Main recorded the
  issue, and subsequent helper deliveries succeeded.
- Keep the local loop status as `progress` until the next regenerated E2E
  finishes with no live issues and no accepted proposals.
