# AgentOrchestra Contract And Finalization Handoff

## Baseline

- Preserved baseline branch/tag: `version-1.0.0` / `v1.0.0`.
- Baseline commit: `548b112 AgentOrchestraのE2E提案を反映`.
- Active work branch: `feature/agent-orchestra-network-contract`.

## Implemented In This Branch

- Synchronized accepted `AgentOrchestra/` changes into the root runtime,
  templates, Skills, SPEC, tests, workflow, and PR template.
- Updated the release evidence surface beyond the original network-contract
  focus to cover finalization, change-control, and retirement readiness:
  - candidate-ledger dispositions block premature `done`;
  - change units require SPEC traceability, checks, reviewers, blocking
    objections, and resolution evidence;
  - non-trivial scoped work requires SubAgent use or a recorded sufficiency
    rationale before `ready_for_review`;
  - accepted ProfessionalAgent retirement requires `retired`, `/exit`, pane
    verification, and `kill-pane` cleanup when needed.
- Added equal-editing AgentTeam startup contracts:
  - MainAgent is the user-facing steward.
  - ProfessionalAgents may edit, review, request changes, and raise blocking
    objections.
  - Pro-to-Pro consultation is normal review evidence.
- Added structured `[Candidates]` ledger support to the shared task file.
  `done` with unresolved candidates wakes MainAgent instead of going quiet.
- Split candidate-ledger parsing and disposition checks out of shared task-file
  parsing so the runtime remains small and responsibility-limited.
- Added `agent_orchestra_minimal.tmux_send` to make tmux text delivery a
  send/capture/retry operation instead of paste-and-hope.
- Tightened tmux delivery confirmation so stale pane activity is not accepted
  unless it is tied to the sent message or a prompt marker.
- Tightened Hook wake delivery freshness so an older identical `runtime_wake`
  capture cannot be accepted as proof that a newly sent wake was delivered.
- Hardened generated Codex config path handling:
  - workspace and Hook state path keys are TOML-escaped before writing
    `agent-orchestra.config.toml`;
  - a regression covers run paths containing double quotes.
- Hardened tmux target boundaries:
  - launch metadata, Agent state, Hook wake, and peer-send delivery accept only
    deterministic `%pane` targets;
  - invalid explicit pane env never falls back to a mutable persisted state
    target;
  - active ProfessionalAgents with a missing or invalid own pane env can wake
    the launch-provided Main pane fallback for repair;
  - `tmux_targets.py` is included in the installed runtime copy list.
- Split added contract coverage so Python source files remain at or below the
  SPEC hard 300-line limit.

## Current Verification

- Latest generated-copy checks after the 2026-06-19 MainAgent self-exit
  command-boundary guard:
  - 2026-06-19 Layer16 runtime review found that the packaged MainAgent
    self-exit helper only submitted `/exit` while `pane_current_command` was
    exactly `node`. That preserved safety for npm-based Codex CLI installs but
    could reject native Codex CLI panes reporting `codex`, leaving a
    user-requested self-exit requirement unresolved before bounded `/exit`
    attempts began.
  - SPEC sections: MainAgent Lifecycle And Self-Exit; Completion Criteria;
    Release Evidence And SPEC Traceability.
  - owner_dri/reviewers: `pro-runtime-16` owned the runtime guard. A bounded
    consultation to `pro-qa-15` was attempted but not accepted while that pane
    was busy; consultation to `pro-env-22` was accepted through
    `agent_orchestra_minimal.tmux_send` for completion/environment review.
  - affected scope: `.codex/agent_orchestra_minimal/self_exit.py`,
    `tests/test_self_exit.py`, `SPEC.md`,
    `.codex/agent_orchestra_minimal/agent_templates/main.AGENTS.md`,
    `.codex/skills/agent-orchestra-tmux-main/SKILL.md`,
    `tests/test_skill_boundary_contract.py`, and `Handoff.md`.
  - required checks after the patch: `python3 -m unittest tests.test_self_exit
    tests.test_skill_boundary_contract tests.test_spec_contract` passed;
    `python3 -m py_compile .codex/agent_orchestra_minimal/self_exit.py
    tests/test_self_exit.py tests/test_skill_boundary_contract.py
    tests/test_spec_contract.py` passed.
  - candidate-ledger disposition: integrated for the native Codex CLI
    self-exit command-boundary candidate; evidence: this handoff entry,
    `.codex/agent_orchestra_minimal/self_exit.py`, and
    `tests/test_self_exit.py`.
  - deterministic finalization blockers: none known for this scoped runtime
    guard after targeted verification; full run status remains `progress`
    until the AgentTeam finishes the broader self-improvement E2E sweep.
  - blocking objections: none known at the time this evidence was recorded.
- Latest generated-copy checks after the 2026-06-19 self-improvement E2E
  integration sweep:
  - 2026-06-19 MainAgent continued the user-requested self-improvement E2E
    against the generated copy at
    `${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra`; the parent
    `AgentOrchestra-dev` repo was kept outside the edit scope.
  - SPEC sections: tmux Communication; MainAgent tmux Authority; Shared Task
    File; Environment cleanup; Release Evidence And SPEC Traceability;
    Completion Criteria.
  - owner_dri/reviewers: MainAgent owned final integration and verification;
    `pro-runtime-16`, `pro-qa-15`, and `pro-env-22` were launched for runtime,
    QA/completion, and environment autonomy review. Initial delivery was
    accepted for all three panes, with degraded delivery observed for
    `pro-qa-15` and `pro-env-22`.
  - affected scope: `.codex/agent_orchestra_minimal/tmux_send.py`,
    `.codex/agent_orchestra_minimal/doctor.py`,
    `.codex/agent_orchestra_minimal/doctor_codex.py`,
    `.codex/agent_orchestra_minimal/launch_io.py`,
    `.codex/agent_orchestra_minimal/self_exit.py`,
    `.codex/agent_orchestra_minimal/server_process_runtime.py`,
    `.codex/skills/agent-orchestra-self-improvement-e2e/SKILL.md`,
    `.codex/skills/agent-orchestra-tmux-common/SKILL.md`,
    `.codex/skills/agent-orchestra-tmux-main/SKILL.md`, `SPEC.md`, and tests.
  - implemented candidates: tmux delivery `--result-json` evidence for retry
    counts and degraded delivery; `server_process` owner/cleanup manifest
    evidence with quoted cleanup commands; `doctor --server-processes` live
    helper owner/cleanup reporting; `self_exit` support for Codex panes whose
    `pane_current_command` is `codex`; copied self-improvement prompts must use
    `.tmp/self-improvement-e2e/status`; `Something went wrong` Codex TUI
    screens are treated as interrupted-recovery targets; `doctor_codex.py`
    split and installed runtime manifest coverage.
  - required checks after the patch: `python3 -m unittest discover -s tests`
    passed, 378 tests; `find .codex/agent_orchestra_minimal .codex/hooks tests
    -name '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check` passed; `python3 .codex/agent_orchestra_minimal/cli.py doctor
    --target-project . --mcp` passed with Playwright MCP present; `nix flake
    check --no-build path:.` passed; `nix build
    path:.#checks.aarch64-darwin.source-contract --no-link` passed.
  - observed E2E issues: `pro-qa-15` initial assignment required 2 submit
    attempts and `pro-env-22` required 3; recovery follow-up to
    `pro-runtime-16` and `pro-env-22` after Codex TUI "Something went wrong"
    screens was not accepted before the recovery-pattern fix. These are
    recorded as E2E operational evidence; the implemented `--result-json` path
    gives future runs durable evidence for the same class of degraded delivery.
  - candidate-ledger disposition: integrated for the tmux delivery result-json
    evidence candidate, server-process owner/cleanup evidence candidate,
    self-exit codex-command candidate, self-improvement status-path candidate,
    interrupted-recovery screen candidate, and doctor split/install manifest
    candidate.
  - deterministic finalization blockers after this scoped sweep: none known
    after full verification, MCP diagnostics, and source-contract build.
  - blocking objections: none known from accepted review evidence; two
    ProfessionalAgent panes hit Codex TUI recovery failures and their partial
    findings were accepted only where backed by MainAgent verification.
- Latest AgentTeam sweep after the 2026-06-08 live SPEC mirror verification pass:
  - 2026-06-08 MainAgent coordinated a live AgentTeam sweep for the user goal
    to read `SPEC.md` and improve `AgentOrchestra/` until no in-scope
    improvements remain. The smallest sufficient team was MainAgent plus
    `pro-runtime-08` for backend/runtime gap analysis and `pro-quality-15` for
    QA/release-evidence review.
  - SPEC sections: Team Execution Sufficiency; Shared Task File; Release
    Evidence And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned coordination and final integration
    evidence; `pro-runtime-08` reviewed runtime implementation gaps and
    generated-copy drift; `pro-quality-15` reviewed launch, task-state,
    tmux-delivery, and release-evidence contracts. Both ProfessionalAgent
    task deliveries were accepted by `agent_orchestra_minimal.tmux_send`.
  - affected scope: `Handoff.md` and
    `tests/test_handoff_release_evidence.py`; runtime source and
    `AgentOrchestra/` mirror content were inspected but no runtime patch was
    warranted by the evidence.
  - required checks run in this cycle: `python3 -m unittest discover -s tests`
    passed, 257 tests; `python3 -m py_compile` over
    `.codex/agent_orchestra_minimal/*.py` passed; root-vs-`AgentOrchestra/`
    mirror comparisons for runtime, tests, `SPEC.md`, README files,
    `Handoff.md`, PR template, and workflow showed no drift except ignored
    `__pycache__`; `pro-quality-15` reported `nix flake check --no-build
    path:$PWD` passed and `nix build
    path:$PWD#checks.$system.source-contract --no-link` passed.
  - candidate-ledger disposition: integrated for the live SPEC mirror
    verification evidence candidate; evidence: this handoff entry,
    `tests/test_handoff_release_evidence.py`, accepted tmux delivery logs for
    `pro-runtime-08` and `pro-quality-15`, and the full unittest output.
  - deterministic finalization blockers for this scoped sweep: none known
    after full verification and mirror consistency checks.
  - blocking objections: none known at the time this evidence was recorded.
- Latest implementation follow-up after the 2026-06-08 safe equals-form extra-arg sweep:
  - 2026-06-08 MainAgent review found one runtime ergonomics candidate in the
    `codex_args` boundary validator: unsafe equals-form runtime overrides such
    as `--profile=agent-orchestra`, `--enable=prevent_idle_sleep`, `--cd=...`,
    and `--add-dir=...` are already rejected, but safe value options such as
    `--model=gpt-5.5`, `-m=gpt-5.5`, and
    `-c=model_reasoning_effort=high` should be accepted just like their split
    forms. This was not a safety hole, but it was an in-scope runtime usability
    improvement candidate.
  - SPEC sections: Instruction Isolation; Launch Skill; Release Evidence And
    SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent identified the candidate during the
    continuous improvement sweep. Runtime implementation edit was attempted in
    the isolated session but deferred because root `.codex/` was read-only; the
    follow-up implementation was applied in the writable root after E2E exit.
  - affected scope: `.codex/agent_orchestra_minimal/launch_args.py`
    and `tests/test_launch_args.py`.
  - required checks run after the follow-up patch: targeted
    `python3 -m unittest tests.test_launch_args
    tests.test_handoff_release_evidence` passed; full verification is recorded
    in the improvement-cycle runner output.
  - candidate-ledger disposition: integrated for the safe equals-form
    `codex_args` candidate; evidence: this handoff entry and
    `tests/test_launch_args.py`.
  - deterministic finalization blockers for this scoped follow-up: none known.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 PR finalization disposition contract guard:
  - 2026-06-08 Layer25 documentation/release-evidence review found that the
    PR template already required final improvement-candidate sweep evidence,
    but the executable change-control test did not assert the terminal
    disposition vocabulary (`integrated`, `rejected`, `deferred`, `blocked`,
    `out-of-scope`, `needs_user`, or added to `[Backlog]`) together with the
    blocking-objection evidence surface. Change-unit evidence is recorded
    only when this finalization vocabulary and objection evidence stay visible
    in the PR checklist contract.
  - SPEC sections: Release Evidence And SPEC Traceability; Completion
    Criteria; Shared Task File.
  - owner_dri/reviewers: `pro-docs` owned this documentation contract guard;
    peer consultation with `pro-runtime` was not required because the change is
    limited to PR-template evidence assertions and handoff traceability, with
    no runtime behavior change.
  - affected scope: `Handoff.md` and `tests/test_change_control_surface.py`.
  - required checks after the patch: targeted `python3 -m unittest
    tests.test_change_control_surface` passed; scoped whitespace check
    `git diff --check -- AgentOrchestra` passed.
  - candidate-ledger disposition: integrated for the PR finalization
    disposition contract candidate; evidence: this handoff entry and
    `tests/test_change_control_surface.py`.
  - deterministic finalization blockers: none known for this scoped
    documentation contract guard after targeted verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 task-file doctor finalization guard:
  - 2026-06-08 MainAgent review found that the shared task file is the SPEC
    source of truth for liveness and quiet completion, but `doctor` could only
    check environment/Codex prerequisites and could not directly report
    deterministic task-file finalization blockers before an operator accepted a
    run as quiet.
  - SPEC sections: Shared Task File; Hook-Driven Re-kick; Release Evidence And
    SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned this runtime/QA guard. `pro-runtime-16`
    and `pro-qa-15` independently reviewed adjacent SPEC/runtime and
    CI/release surfaces in the same cycle; no blocking objection was raised.
  - affected scope: `.codex/agent_orchestra_minimal/doctor.py`,
    `.codex/agent_orchestra_minimal/cli.py`, `README.md`, `README.ja.md`,
    `Handoff.md`, and `tests/test_codex_config_contract.py`.
  - required checks after the patch: `python3 -m unittest
    tests.test_codex_config_contract tests.test_readme_verification_contract`
    passed, 18 tests; `python3 -m py_compile
    .codex/agent_orchestra_minimal/doctor.py
    .codex/agent_orchestra_minimal/cli.py
    tests/test_codex_config_contract.py` passed; `python3 -m unittest discover
    -s tests` passed, 254 tests; `find .codex/agent_orchestra_minimal
    .codex/hooks tests -name '*.py' -print0 | xargs -0 python3 -m py_compile`
    passed; scoped whitespace check passed; path-form `nix flake check
    --no-build path:$PWD` passed from `AgentOrchestra/`.
  - candidate-ledger disposition: integrated for the task-file doctor
    finalization guard candidate; evidence: this handoff entry,
    `doctor --task-file`, and `tests/test_codex_config_contract.py`.
  - deterministic finalization blockers: none known for this scoped guard after
    full verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 E2E evidence CI gate guard:
  - 2026-06-08 Layer15 QA/change-control review found that `E2E.md`
    is part of SPEC completion evidence and PR residual-risk evidence, but the
    current source-contract workflow path filters and whitespace check excluded
    `E2E.md`. That let evidence-only E2E updates bypass the CI/release
    evidence gate even though an older E2E run had accepted this control.
  - SPEC sections: Development Process; Release Evidence And SPEC
    Traceability; Completion Criteria.
  - owner_dri/reviewers: `pro-qa-15` owned this QA/release guard. Peer
    consultation with `pro-runtime-16` was attempted through tmux after the
    patch, but delivery was not accepted because the peer pane remained busy;
    no runtime approval is claimed. The change is a narrow CI evidence-surface
    regression fix, mirrors previously accepted E2E evidence, and changes no
    runtime behavior.
  - affected scope: `.github/workflows/agent-orchestra-source-contract.yml`,
    `.github/pull_request_template.md`, `Handoff.md`, and
    `tests/test_change_control_surface.py`.
  - required checks after the patch: `python3 -m unittest
    tests.test_change_control_surface` passed, 5 tests; `python3 -m unittest
    tests.test_change_control_surface tests.test_handoff_release_evidence`
    passed, 10 tests; `python3 -m unittest discover -s tests` passed, 254
    tests; `find .codex/agent_orchestra_minimal .codex/hooks tests -name
    '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check -- AgentOrchestra` passed from the parent repo; path-form `nix
    flake check --no-build path:$PWD` passed from `AgentOrchestra/`;
    `nix build path:$PWD#checks.aarch64-darwin.source-contract --no-link`
    passed.
  - candidate-ledger disposition: integrated for the E2E evidence CI gate
    candidate; evidence: this handoff entry, workflow path filters, PR
    checklist, and `tests/test_change_control_surface.py`.
  - deterministic finalization blockers: none known for this scoped QA guard
    after targeted verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 Codex feature parser absent-state guard:
  - 2026-06-08 Layer16 runtime review found that `codex features list` prose
    such as `prevent_idle_sleep is not supported`, `prevent_idle_sleep
    unavailable`, or `unknown feature prevent_idle_sleep` could be parsed as
    `present`, causing the launcher to add `--enable prevent_idle_sleep` even
    when the feature was explicitly unusable.
  - 2026-06-08 MainAgent runtime review found that user-supplied Codex extra
    args rejected boundary overrides in split-token form, but the ignored public
    copy also needed to reject equals-form runtime boundary overrides such as
    `--profile=agent-orchestra`, `--enable=prevent_idle_sleep`, `--cd=...`,
    and `--add-dir=...`.
  - SPEC sections: Instruction Isolation; Skills; Release Evidence And SPEC
    Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent identified the safety edge case;
    `pro-runtime-spec` independently confirmed it as a runtime-contract gap.
    The initial tmux delivery to Main was not accepted while Main was busy, so
    the pane capture is treated as review evidence rather than a delivered
    instruction.
  - ProfessionalAgent sufficiency/retirement disposition: the scoped runtime
    guard used the smallest sufficient team for a narrow runtime-contract
    parser change, MainAgent plus one Layer16 runtime reviewer; no additional
    ProfessionalAgent or SubAgent viewpoint was required because the affected
    surface was limited to feature parsing and launch-argument contract tests.
    Accepted-retirement evidence is not claimed in this public-copy handoff
    entry; until MainAgent accepts the result, the ProfessionalAgent review
    remains review evidence rather than a retired-pane record.
  - affected scope: `.codex/agent_orchestra_minimal/codex_features.py`,
    `tests/test_codex_config_contract.py`, `tests/test_launch_args.py`, and
    `Handoff.md` inside the ignored `AgentOrchestra/` public copy. The E2E
    isolated session recorded root mirror synchronization separately because
    that session could not write root `.codex` files directly.
  - required checks after the patch: `python3 -m unittest
    tests.test_codex_config_contract tests.test_launch_args` passed;
    `python3 -m py_compile .codex/agent_orchestra_minimal/codex_features.py
    tests/test_codex_config_contract.py tests/test_launch_args.py` passed;
    `python3 -m unittest tests.test_handoff_release_evidence` passed;
    `python3 -m unittest discover -s tests` passed, 249 tests; `find
    .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0 |
    xargs -0 python3 -m py_compile` passed; `git diff --check --
    AgentOrchestra` passed from the parent repo; `nix flake check --no-build
    path:$PWD` passed from `AgentOrchestra/`.
  - candidate-ledger disposition: integrated for the Codex feature parser
    absent-state guard candidate and the equals-form launch-boundary override
    guard candidate; evidence: this handoff entry,
    `.codex/agent_orchestra_minimal/codex_features.py`,
    `.codex/agent_orchestra_minimal/launch_args.py`,
    `tests/test_codex_config_contract.py`, and `tests/test_launch_args.py`.
  - deterministic finalization blockers: none known for the public-copy runtime
    guard after targeted verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 Issue #7 E2E current-test evidence guard:
  - 2026-06-08 Layer25 documentation/release-evidence review found that
    `E2E.md` still named removed Issue #7 acceptance modules
    `tests/test_wake_payload_contract.py`,
    `tests.test_wake_payload_contract`, and
    `tests.test_e2e_issue7_acceptance`, while the current executable
    long-run-equivalent contract evidence lives in
    `tests/test_continuous_improvement_contract.py` with related Hook/tmux and
    Skill contract tests.
  - SPEC sections: GitHub Issue #7: Long-Run Memory Dilution; Release
    Evidence And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: `pro-docs-release` owned this documentation evidence
    guard; peer consultation was not required because the change only updates
    stale E2E evidence names and adds an executable documentation assertion,
    with no runtime behavior change.
  - affected scope: `E2E.md`, `Handoff.md`,
    `tests/test_continuous_improvement_contract.py`, and
    `tests/test_change_control_surface.py`.
  - required checks after the patch: `python3 -m unittest
    tests.test_continuous_improvement_contract tests.test_change_control_surface
    tests.test_handoff_release_evidence tests.test_readme_verification_contract`
    passed, 21 tests; `python3 -m py_compile
    tests/test_continuous_improvement_contract.py` passed; `python3 -m unittest
    discover -s tests` passed, 246 tests; `find
    .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0 |
    xargs -0 python3 -m py_compile` passed; `git diff --check --
    AgentOrchestra` passed from the parent repo; path-form `nix flake check
    --no-build path:$PWD` passed on `aarch64-darwin`.
  - candidate-ledger disposition: integrated for the Issue #7 E2E current-test
    evidence guard candidate; evidence: this handoff entry, `E2E.md`, and
    `tests/test_continuous_improvement_contract.py`.
  - deterministic finalization blockers: none known for this scoped docs
    evidence guard after standard verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 README verification contract guard:
  - 2026-06-08 Layer15 QA/change-control review found that README contributor
    verification was already aligned in content, but the executable README
    contract test did not strongly guard the full standard verification
    surface across English and Japanese docs, including path-form Nix line
    wrapping.
  - SPEC sections: Development Process And Quality Gates; Release Evidence
    And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: `pro-qa-15` owned this QA guard; peer consultation
    with `pro-runtime` was attempted through tmux but not delivered because
    the peer pane remained busy, so no runtime approval is claimed. The change
    is limited to documentation contract evidence and does not alter runtime
    behavior.
  - affected scope: `Handoff.md`, `tests/test_change_control_surface.py`, and
    `tests/test_readme_verification_contract.py`.
  - required checks after the patch: `python3 -m unittest
    tests.test_readme_verification_contract tests.test_change_control_surface`
    passed, 6 tests; `python3 -m py_compile
    tests/test_readme_verification_contract.py` passed; `python3 -m unittest
    discover -s tests` passed, 245 tests; `find
    .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0 |
    xargs -0 python3 -m py_compile` passed; `git diff --check --
    AgentOrchestra` passed from the parent repo; path-form `nix flake check
    --no-build path:$PWD` passed on `aarch64-darwin`.
  - candidate-ledger disposition: integrated for the README verification
    contract guard candidate; evidence: this handoff entry and
    `tests/test_readme_verification_contract.py`.
  - deterministic finalization blockers: none known for this scoped QA guard
    after standard verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 path-form README evidence guard:
  - 2026-06-08 Layer15 QA/change-control review found that SPEC Completion
    Criteria and the PR checklist require path-form Nix evidence for
    generated-copy or untracked-fixture verification, but README contributor
    verification only showed repository-root Nix commands.
  - SPEC sections: Development Process And Quality Gates; Release Evidence
    And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: `pro-qa-15` owned this QA docs/test guard; peer
    consultation was not required because the change is limited to contributor
    verification wording and executable documentation assertions, with no
    runtime behavior change.
  - affected scope: `README.md`, `README.ja.md`, `Handoff.md`,
    `tests/test_readme_verification_contract.py`, and
    `tests/test_change_control_surface.py`.
  - required checks after the patch: `python3 -m unittest
    tests.test_readme_verification_contract tests.test_change_control_surface`
    passed, 6 tests; `python3 -m unittest discover -s tests` passed, 245
    tests; `find .codex/agent_orchestra_minimal .codex/hooks tests -name
    '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check -- AgentOrchestra` passed from the parent repo; `nix flake check
    --no-build path:$PWD` passed; `nix build
    path:$PWD#checks.$system.source-contract` passed.
  - candidate-ledger disposition: integrated for the path-form README evidence
    candidate; evidence: this handoff entry, README verification docs, and
    `tests/test_readme_verification_contract.py`.
  - deterministic finalization blockers: none known for this scoped QA docs
    guard after targeted verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 prevent-idle-sleep launch guard:
  - 2026-06-08 MainAgent, `pro-runtime-08`, and `pro-docs-25` reviewed
    `SPEC.md` against the current generated-copy runtime and found that the
    automatic Codex `prevent_idle_sleep` launch behavior had runtime and README
    coverage but no freshest release-evidence entry.
  - SPEC sections: Instruction Isolation; Skills; Release Evidence And SPEC
    Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned this evidence refresh; `pro-runtime-08`
    reviewed launch/runtime behavior and full unittest status; `pro-docs-25`
    identified the release-evidence freshness gap.
  - affected scope: `Handoff.md`, `tests/test_change_control_surface.py`,
    `tests/test_handoff_release_evidence.py`, and
    `tests/test_readme_verification_contract.py`.
  - required checks before this evidence refresh: `python3 -m unittest
    discover -s tests` passed, 245 tests.
  - required checks after this evidence refresh: `python3 -m unittest
    tests.test_change_control_surface tests.test_handoff_release_evidence
    tests.test_readme_verification_contract` passed, 10 tests; `python3 -m unittest
    tests.test_launch_args tests.test_codex_config_contract tests.test_spec_contract`
    passed, 37 tests; `python3 -m unittest discover -s tests` passed, 245
    tests; `find .codex/agent_orchestra_minimal .codex/hooks tests -name
    '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check -- AgentOrchestra` passed from the parent repo; `nix flake check
    path:${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra --no-build`
    passed.
  - candidate-ledger disposition: integrated for the prevent-idle-sleep
    release-evidence freshness candidate; evidence: this handoff entry,
    `SPEC.md`, `README.md`, `.codex/agent_orchestra_minimal/launch_args.py`,
    `.codex/agent_orchestra_minimal/codex_features.py`,
    `tests/test_change_control_surface.py`,
    `tests/test_handoff_release_evidence.py`, and
    `tests/test_readme_verification_contract.py`.
  - deterministic finalization blockers: none known for this scoped evidence
    refresh after targeted verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 unittest runner guard:
  - 2026-06-08 Layer15 QA/change-control review found that the generated-copy
    CI workflow and SPEC required `unittest`, but contributor docs and the PR
    checklist did not explicitly prevent release evidence from drifting toward
    `pytest`, which is not a project dependency.
  - SPEC sections: Development Process And Quality Gates; Release Evidence
    And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: `pro-qa-15` owned this QA guard; peer consultation was
    not required because the change is limited to contributor verification
    wording and change-control assertions, with no runtime behavior change.
  - affected scope: `README.md`, `README.ja.md`,
    `.github/pull_request_template.md`, `Handoff.md`, and
    `tests/test_change_control_surface.py`.
  - required checks after the patch: `python3 -m unittest
    tests.test_change_control_surface` passed, 10 tests; `python3 -m unittest
    discover -s tests` passed, 245 tests; `find
    .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0 |
    xargs -0 python3 -m py_compile` passed; `git diff --check --
    AgentOrchestra` passed from the parent repo.
  - candidate-ledger disposition: integrated for the unittest runner guard
    candidate; evidence: this handoff entry, README verification docs, PR
    template checklist, and `tests/test_change_control_surface.py`.
  - deterministic finalization blockers: none known for this scoped QA guard
    after standard verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-08 SPEC alignment sweep:
  - 2026-06-08 MainAgent, `pro-runtime-16`, and `pro-qa-15` reviewed
    `SPEC.md` against the generated-copy `AgentOrchestra/` runtime, tests,
    docs, and release evidence surfaces. The generated copy is content-synced
    with the parent runtime surfaces, but it is not tracked by the parent Git
    worktree, so release checks must record path-form Nix evidence when run
    against this copy directly.
  - The runtime review found one tmux liveness gap: pre-send readiness treated
    `MainAgent` and `ProfessionalAgent` prompts as occupied but did not treat
    direct ProfessionalAgent id prompts such as `pro-runtime-16 -> pro-qa-15:`
    as occupied. The prompt classifier now treats those peer-consultation
    prompts as pending Agent messages before paste/send.
  - The QA/change-control review found one contributor evidence gap:
    release-process docs and the PR checklist required `unittest` but did not
    explicitly prevent silent substitution with `pytest`. README and PR
    evidence now preserve `unittest` as the project runner unless a task adds
    and justifies a new dependency.
  - SPEC sections: Development Process And Quality Gates; Shared Task File;
    Hook-Driven Re-kick; tmux Communication; Instruction Isolation; Release
    Evidence And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned the handoff evidence refresh and
    integration review; `pro-runtime-16` owned the tmux peer-prompt guard and
    reviewed runtime/task/tmux/launch surfaces; `pro-qa-15` owned the
    `unittest` release-evidence guard and reviewed QA/change-control/release
    surfaces.
  - affected scope: `.codex/agent_orchestra_minimal/tmux_probe.py`,
    `tests/test_tmux_send.py`, `.github/pull_request_template.md`,
    `README.md`, `README.ja.md`, `Handoff.md`, and
    `tests/test_change_control_surface.py`.
  - required checks before this evidence refresh: `python3 -m unittest
    discover -s tests` passed, 244 tests; `python3 -m py_compile $(find
    .codex -name '*.py' -type f | sort)` passed; `git diff --check --
    AgentOrchestra` passed from the parent repo; direct `nix flake check
    --no-build` inside `AgentOrchestra/` failed because the parent Git
    worktree does not track `AgentOrchestra/flake.nix`; path-form `nix flake
    check path:${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra
    --no-build` passed.
  - required checks after integrating the scoped improvements: `python3 -m
    unittest tests.test_tmux_send tests.test_tmux_send_edge_cases` passed, 28
    tests; `python3 -m unittest tests.test_change_control_surface` passed, 10
    tests; `python3 -m unittest discover -s tests` passed, 245 tests;
    `python3 -m py_compile $(find .codex -name '*.py' -type f | sort)`
    passed; `git diff --check -- AgentOrchestra` passed; path-form `nix flake
    check path:${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra
    --no-build` passed; path-form `nix build
    path:${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra#checks.$(nix
    eval --raw --impure --expr builtins.currentSystem).source-contract
    --no-link` passed.
  - candidate-ledger disposition: integrated for the SPEC alignment evidence
    refresh candidate, the tmux peer-prompt guard candidate, and the
    `unittest` release-evidence guard candidate; evidence: this handoff entry,
    `tests/test_change_control_surface.py`, `tests/test_tmux_send.py`, and
    `.codex/agent_orchestra_minimal/tmux_probe.py`.
  - deterministic finalization blockers: none known for this scoped evidence
    refresh after standard and path-form Nix verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-07 tmux delivery baseline guard:
  - 2026-06-07 live AgentOrchestra E2E run found a second tmux delivery
    false-acceptance risk: after a fresh pasted message disappeared back to a
    ready prompt, the helper could accept a capture identical to the baseline
    screen if that old screen still contained a stale activity marker.
  - SPEC sections: tmux Communication; Hook-Driven Re-kick; Release Evidence
    And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned the runtime fix; `runtime-pro`
    provided the blocking runtime objection; `docs-pro` reviewed docs/contracts
    and found no additional drift.
  - affected scope: `.codex/agent_orchestra_minimal/tmux_delivery.py`,
    `tests/test_tmux_send_edge_cases.py`, `Handoff.md`, and
    `tests/test_change_control_surface.py`.
  - required checks after the patch: `python3 -m unittest
    tests.test_tmux_send_edge_cases` passed, 13 tests; `python3 -m unittest
    discover -s tests` passed, 244 tests; `python3 -m py_compile
    .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py` passed;
    `git diff --check` passed.
  - candidate-ledger disposition: integrated for the tmux delivery baseline
    false-acceptance candidate; evidence: this handoff entry,
    `tests/test_change_control_surface.py`, and
    `tests/test_tmux_send_edge_cases.py`.
  - deterministic finalization blockers: none known for this scoped runtime
    patch after standard verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-07 QA/release evidence consistency pass:
  - 2026-06-07 Layer15 QA/release-process review re-ran the standard
    source-contract checks and found release-evidence drift: the latest handoff
    evidence still named the earlier 238-test generated-copy run while the
    current suite now runs 242 tests.
  - The same SPEC sweep found that `agent-orchestra-release` existed in
    `.codex/skills` and SPEC's Release Skill section, but generated isolated
    `CODEX_HOME/skills` material did not install it for Agents that are
    explicitly assigned a release workflow.
  - SPEC sections: Development Process And Quality Gates; Shared Task File;
    Hook-Driven Re-kick; tmux Communication; Instruction Isolation; Release
    Evidence And SPEC Traceability; Skills; Completion Criteria.
  - owner_dri/reviewers: `pro-qa-15` owned the evidence consistency pass;
    MainAgent owned the release-skill launch-material fix; the two changes were
    reviewed together during the same AgentTeam cycle.
  - affected scope: `.codex/agent_orchestra_minimal/launch_io.py`,
    `tests/test_launch_material_install_contract.py`, `Handoff.md`, and
    `tests/test_change_control_surface.py`.
  - required checks before the patch: `python3 -m unittest discover -s tests`
    passed, 242 tests; `find .codex/agent_orchestra_minimal .codex/hooks tests
    -name '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check -- AgentOrchestra` passed.
  - required checks after the patch: `python3 -m unittest
    tests.test_change_control_surface` passed, 9 tests; `python3 -m unittest
    tests.test_launch_material_install_contract` passed, 7 tests; `python3 -m
    unittest discover -s tests` passed, 243 tests; `python3 -m py_compile
    .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py` passed;
    `git diff --check -- AgentOrchestra` passed; `nix flake check
    path:${AGENT_ORCHESTRA_DEV_ROOT}/AgentOrchestra` passed
    `checks.aarch64-darwin.source-contract`.
  - candidate-ledger disposition: integrated for the QA/release evidence drift
    candidate and the release-skill launch-material install candidate;
    evidence: this handoff entry, `tests/test_change_control_surface.py`, and
    `tests/test_launch_material_install_contract.py`.
  - deterministic finalization blockers: none known for this scoped evidence
    consistency patch after standard verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-07 tmux delivery confirmation fix:
  - 2026-06-07 live AgentOrchestra E2E run found a runtime delivery
    false-positive: `tmux_send` reported an accepted task for `pro-runtime-08`
    while the message was still visibly queued at the Codex prompt and required
    a manual submit key to start.
  - SPEC sections: tmux Communication; Hook-Driven Re-kick; Release Evidence
    And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned the runtime fix; `pro-runtime-08` and
    `pro-qa-15` provided independent runtime and QA review evidence during the
    same E2E cycle.
  - affected scope: `.codex/agent_orchestra_minimal/tmux_delivery.py`,
    `tests/test_tmux_send_edge_cases.py`, `Handoff.md`, and
    `tests/test_change_control_surface.py`.
  - required checks after the patch: `python3 -m unittest discover -s tests`
    passed, 238 tests; `find .codex/agent_orchestra_minimal .codex/hooks tests
    -name '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check -- AgentOrchestra` passed.
  - candidate-ledger disposition: integrated for the tmux delivery
    false-positive candidate; evidence: `.codex/agent_orchestra_minimal/
    tmux_delivery.py`, `tests/test_tmux_send_edge_cases.py`, and this handoff
    entry.
  - deterministic finalization blockers: none known for this scoped runtime
    delivery fix after standard verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-06-07 QA evidence refresh:
  - 2026-06-07 Layer15 QA/release-process review found release-evidence drift:
    the newest handoff evidence still named the earlier 215-test generated-copy
    run even though the current source-contract suite now runs 233 tests.
  - SPEC sections: Release Evidence And SPEC Traceability; Completion
    Criteria.
  - owner_dri/reviewers: `pro-qa-15` owned this evidence refresh; peer
    consultation with `pro-runtime-08` was not required because this change unit
    only updates QA evidence text and its contract assertion after a passing
    source-contract run.
  - affected scope: `Handoff.md` and `tests/test_change_control_surface.py`.
  - required checks before the patch: `python3 -m unittest discover -s tests`
    passed, 233 tests; `find .codex/agent_orchestra_minimal .codex/hooks tests
    -name '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check -- AgentOrchestra` passed.
  - required checks after the patch: `python3 -m unittest discover -s tests`
    passed, 235 tests; `find .codex/agent_orchestra_minimal .codex/hooks tests
    -name '*.py' -print0 | xargs -0 python3 -m py_compile` passed; `git diff
    --check -- AgentOrchestra` passed.
  - candidate-ledger disposition: integrated for the Handoff verification-count
    drift candidate; evidence: this handoff entry and
    `tests/test_change_control_surface.py`.
  - deterministic finalization blockers: none known for this scoped QA evidence
    refresh after standard verification.
  - blocking objections: none known.
- Latest generated-copy checks after the 2026-05-27 launch profile and release-skill boundary pass:
  - 2026-05-27 SPEC review found three launch/change-control gaps in the
    generated-copy surface: launch metadata still referenced legacy
    `--profile-v2`; installed launch material did not assert private
    permissions for generated runtime/auth/config files; and the project-local
    release Skill needed to be documented as explicit operator guidance rather
    than part of the default minimal runtime launch contract.
  - SPEC sections: Instruction Isolation; Skills; Development Policy; Release
    Evidence And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent coordinated this pass with
    `pro-runtime-16` and `pro-docs-25` ProfessionalAgent review panes for
    runtime and documentation consistency.
  - affected scope: `.codex/agent_orchestra_minimal/launch_args.py`,
    `.codex/agent_orchestra_minimal/launch_io.py`,
    `.codex/agent_orchestra_minimal/launch_material.py`,
    `.codex/skills/agent-orchestra-launch/SKILL.md`,
    `.github/workflows/agent-orchestra-source-contract.yml`, `SPEC.md`,
    `tests/test_launch_args.py`, `tests/test_launch_material_install_contract.py`,
    `tests/test_spec_contract.py`, and this handoff evidence.
  - required checks: `python3 -m unittest discover -s tests` passed, 215 tests;
    `python3 -m py_compile .codex/agent_orchestra_minimal/*.py
    .codex/hooks/*.py` passed; `git diff --check` passed.
  - candidate-ledger disposition: integrated for the `--profile` launch
    contract, private launch-material permissions, release Skill boundary, and
    path-form Nix source-contract workflow coverage.
  - deterministic finalization blockers: none known for this change unit after
    full unittest, runtime `py_compile`, whitespace verification, and live
    ProfessionalAgent review.
  - blocking objections: none known at this checkpoint.
- Latest generated-copy checks after the 2026-05-27 tmux probe split:
  - 2026-05-27 E2E found that `tmux_delivery.py` had reached 299 lines after
    the busy-peer guards, making the SPEC hard file-size limit fragile. It also
    exposed that a completed Codex TUI answer may end with a `Worked for`
    footer rather than `Done.`, so the pre-send readiness guard could keep
    treating an input prompt as busy.
  - SPEC sections: Development Process And Quality Gates; tmux Communication;
    Release Evidence And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned the split and readiness follow-up;
    `pro-runtime-08` reviewed runtime/tmux behavior and `pro-qa-15` reviewed
    candidate-ledger contract coverage.
  - affected scope: `.codex/agent_orchestra_minimal/tmux_delivery.py`,
    `.codex/agent_orchestra_minimal/tmux_probe.py`,
    `.codex/agent_orchestra_minimal/launch_io.py`,
    `tests/test_tmux_send.py`, `tests/test_shared_task_file_candidates.py`,
    and `Handoff.md`.
  - required checks: targeted `python3 -m unittest tests.test_tmux_send`
    passed, 15 tests; `python3 -m unittest discover -s tests` passed, 208
    tests; targeted `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-
    split python3 -m py_compile ...` passed for the split runtime and tests.
  - candidate-ledger disposition: integrated for the tmux probe split,
    completed-answer footer readiness guard, existing agent-message prompt
    overwrite guard, and candidate-ledger field coverage.
  - deterministic finalization blockers: final E2E is required because this
    cycle accepted additional runtime/test changes.
  - follow-up during final E2E widened the existing agent-message prompt guard
    to cover named/suffixed `MainAgent` and `ProfessionalAgent` composer
    prompts such as `MainAgent reviewer:` and `ProfessionalAgent role -> peer:`;
    targeted `python3 -m unittest tests.test_tmux_send` passed, 15 tests.
  - follow-up zero-final E2E integrated the ProfessionalAgent
    `ready_for_review` task-file contract: ProfessionalAgent work moves to or
    stays in `[InReview]` until MainAgent accepts or rejects it, rather than
    self-finalizing in `[Done]`; generated-copy full unittest passed, 212
    tests, with SPEC/template/contract-test coverage.
  - blocking objections: none after targeted verification.
- Latest generated-copy checks after the 2026-05-27 README docs gate:
  - 2026-05-27 QA/release-process review found that README contributor
    verification policy changes were not part of the source-contract workflow
    trigger or scoped whitespace release-evidence gate.
  - SPEC sections: Release Evidence And SPEC Traceability; Completion
    Criteria.
  - owner_dri/reviewers: `pro-qa-15` owned the change-control gate patch;
    `pro-runtime-08` consultation was attempted but not accepted while both
    panes were busy, with no delivered blocking objection.
  - affected scope: `.github/workflows/agent-orchestra-source-contract.yml`,
    `.github/pull_request_template.md`, `tests/test_change_control_surface.py`,
    and `Handoff.md`.
  - required checks: generated-copy `python3 -m unittest
    tests.test_change_control_surface` passed, 6 tests; generated-copy
    `python3 -m unittest discover -s tests` passed, 204 tests; generated-copy
    `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-qa15 python3 -m
    py_compile tests/test_change_control_surface.py` passed; tracked-root
    `python3 -m unittest tests.test_change_control_surface` passed, 6 tests;
    tracked-root `PYTHONPYCACHEPREFIX=/private/tmp/
    agent-orchestra-pycache-qa15-root python3 -m py_compile
    tests/test_change_control_surface.py` passed; tracked-root `git diff
    --check -- .github tests Handoff.md README.md README.ja.md SPEC.md`
    passed.
  - candidate-ledger disposition: integrated for the README contributor-doc
    gate candidate; evidence: this handoff entry, `.github/workflows/
    agent-orchestra-source-contract.yml`, `.github/pull_request_template.md`,
    and `tests/test_change_control_surface.py`.
  - deterministic finalization blockers: none known for this scoped QA gate;
    live tmux consultation delivery remained congested and is recorded as
    non-blocking peer-consultation evidence rather than a runtime defect in
    this change unit.
  - blocking objections: none delivered.
- Latest generated-copy checks after the 2026-05-27 prompt-like output guard:
  - 2026-05-27 MainAgent and ProfessionalAgent review found one additional
    tmux liveness edge case: while a peer Codex TUI is still working, an
    assistant output line beginning with ASCII `>` or Unicode `›` can resemble
    a composer prompt and make pre-send readiness too permissive.
  - SPEC sections: tmux Communication; Release Evidence And SPEC
    Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned the focused tmux delivery patch;
    `pro-runtime-08` reviewed runtime/tmux liveness and `pro-sre-22` reviewed
    Stop Hook/finalization evidence.
  - affected scope: `.codex/agent_orchestra_minimal/tmux_delivery.py`,
    `.codex/agent_orchestra_minimal/tmux_wake.py`,
    `tests/test_tmux_send.py`, and `Handoff.md`.
  - required checks: targeted `python3 -m unittest
    tests.test_tmux_send.TmuxSendTests.test_send_text_does_not_treat_busy_ascii_quote_as_ready_prompt
    tests.test_tmux_send.TmuxSendTests.test_send_text_does_not_treat_busy_unicode_quote_as_ready_prompt
    tests.test_tmux_send.TmuxSendTests.test_send_text_waits_for_peer_to_return_to_ready_prompt_before_paste
    tests.test_tmux_send.TmuxSendTests.test_send_text_does_not_paste_while_target_is_working`
    passed, 4 tests; focused `python3 -m unittest
    tests.test_stop_hook_delivery_failure tests.test_stop_hook_and_tmux
    tests.test_tmux_send` passed, 28 tests; `python3 -m unittest discover -s
    tests` passed, 204 tests; `find .codex/agent_orchestra_minimal
    .codex/hooks tests -name '*.py' -print0 | xargs -0 python3 -m py_compile`
    passed; whitespace check for touched files passed; `git diff --check --
    AgentOrchestra` passed; `nix flake check --no-build path:$PWD` passed.
  - candidate-ledger disposition: integrated for the busy prompt-like output
    readiness candidate and bounded wake polling interval; evidence: this
    handoff entry, `tests/test_tmux_send.py`,
    `.codex/agent_orchestra_minimal/tmux_delivery.py`,
    `.codex/agent_orchestra_minimal/tmux_wake.py`, and review panes `%1396` /
    `%1397`.
  - deterministic finalization blockers: none known after full verification,
    task-file finalization, and accepted ProfessionalAgent pane retirement.
  - blocking objections: none after accepting the conservative readiness guard.
- Latest generated-copy checks after the 2026-05-27 busy peer-send guard:
  - 2026-05-27 E2E exposed that peer consultation could target a Codex TUI
    pane while it was still working, leaving one ProfessionalAgent interrupted
    and another state marked `working` after its TUI had returned to `zsh`.
  - SPEC sections: tmux Communication; Release Evidence And SPEC
    Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent accepted the runtime delivery guard as an
    E2E blocker fix; the failed E2E runtime and QA/change-control panes
    (`%1391` / `%1392`) supplied the review evidence.
  - affected scope: `.codex/agent_orchestra_minimal/tmux_delivery.py`,
    `tests/tmux_send_helpers.py`, `tests/test_tmux_send.py`,
    `tests/test_tmux_send_edge_cases.py`,
    `tests/test_stop_hook_delivery_failure.py`, `Handoff.md`, and
    `tests/test_change_control_surface.py`.
  - required checks: targeted `python3 -m unittest tests.test_tmux_send
    tests.test_tmux_send_edge_cases tests.test_tmux_delivery_prompt_status
    tests.test_stop_hook_delivery_failure` passed, 33 tests;
    `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-busy-send
    python3 -m py_compile .codex/agent_orchestra_minimal/tmux_delivery.py
    .codex/agent_orchestra_minimal/tmux_send.py tests/test_tmux_send.py
    tests/tmux_send_helpers.py` passed; `python3 -m unittest discover -s
    tests` passed, 201 tests; `PYTHONPYCACHEPREFIX=/private/tmp/
    agent-orchestra-pycache-busy-send-full python3 -m py_compile $(find
    .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py')` passed;
    `git diff --check -- .codex tests layers Handoff.md SPEC.md .github
    .gitignore flake.nix flake.lock` passed; `nix flake check --no-build
    path:$PWD` passed.
  - candidate-ledger disposition: integrated for the busy peer-send
    interruption candidate; evidence: failed E2E panes `%1388`, `%1391`, and
    `%1392`, this handoff entry, and the tmux delivery regression tests.
  - deterministic finalization blockers: follow-up E2E is required because the
    failed E2E also showed an external `codex_apps` MCP startup timeout and did
    not reach `/exit`.
  - blocking objections: none after accepting the pre-send input-readiness
    guard as the narrow runtime fix.
- Latest generated-copy checks after the 2026-05-26 live AgentTeam review:
  - 2026-05-26 MainAgent launched independent runtime and documentation
    ProfessionalAgent panes (`%1332` / `%1333`) from isolated launch material,
    delivered scoped SPEC review tasks through the tmux send helper, and used
    their review as live AgentTeam evidence for this pass.
  - SPEC sections: Team Execution Sufficiency; tmux Communication; Release
    Evidence And SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: MainAgent owned the release-evidence refresh and final
    blocker sweep; `pro-backend-runtime` reviewed runtime Python/test
    consistency; `pro-docs-spec` reviewed SPEC/docs/skill/test-contract
    consistency.
  - affected scope: `Handoff.md`, `tests/test_change_control_surface.py`,
    `.codex/agent_orchestra_minimal/tmux_delivery.py`, and
    `tests/test_tmux_send_edge_cases.py`.
  - required checks: root follow-up `python3 -m unittest discover -s tests`
    passed, 194 tests after adding the false-negative regression;
    `find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py'
    -print0 | xargs -0 python3 -m py_compile` passed; `git diff --check --
    .codex tests layers Handoff.md SPEC.md .github .gitignore flake.nix
    flake.lock` passed in the generated-copy run.
  - candidate-ledger disposition: integrated in root after accepting the live
    tmux delivery false-negative candidate; evidence: `Handoff.md`,
    `tests/test_change_control_surface.py`, `tests/test_tmux_send_edge_cases.py`,
    `.codex/agent_orchestra_minimal/tmux_delivery.py`, ProfessionalAgent panes
    `%1332` / `%1333`, and the shared task-file candidate ledger for this run.
  - deterministic finalization blockers: none known after applying the
    false-negative fix in the writable root environment; a follow-up E2E is
    required before the local improvement-loop status can become `done`.
  - blocking objections: none after accepting and implementing the runtime
    delivery classifier fix.
- Latest generated-copy checks after the 2026-05-26 SPEC-driven refresh:
  - 2026-05-26 MainAgent evidence refresh compared `SPEC.md` with the current
    generated-copy runtime, tests, Skills, and handoff evidence after
    launching the smallest sufficient review team for this pass.
  - SPEC sections: Release Evidence And SPEC Traceability; Completion
    Criteria; Team Execution Sufficiency.
  - owner_dri/reviewers: MainAgent refreshed current release evidence;
    pro-runtime and pro-requirements are the independent review panes for
    runtime/SPEC consistency; MainAgent kept the final integration and
    finalization-blocker sweep.
  - affected scope: `Handoff.md`,
    `tests/test_change_control_surface.py`, `SPEC.md`,
    `.codex/agent_orchestra_minimal/agent_templates/main.AGENTS.md`, and
    `tests/test_skill_boundary_contract.py`.
  - required checks: `python3 -m unittest discover -s tests` passed, 193 tests;
    `find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py'
    -print0 | xargs -0 python3 -m py_compile` passed; `git diff --check --
    AgentOrchestra` from the parent worktree passed in the generated-copy run.
  - candidate-ledger disposition: integrated in root after accepting the
    blocked generated-copy proposal; evidence:
    `tests/test_change_control_surface.py`, `Handoff.md`, `SPEC.md`,
    `.codex/agent_orchestra_minimal/agent_templates/main.AGENTS.md`,
    `.codex/skills/agent-orchestra-tmux-main/SKILL.md`,
    `tests/test_skill_boundary_contract.py`, and review panes `%1327` /
    `%1328`.
  - deterministic finalization blockers: none known after applying the
    self-exit wording fix in the writable root environment; a follow-up E2E is
    required before the local improvement-loop status can become `done`.
  - blocking objections: none after narrowing the Main template prohibition to
    ad hoc shell job-control self-exit while preserving the bounded detached
    Python Skill procedure.
- Latest generated-copy checks after the final 2026-05-25 integration pass:
  - 2026-05-25 MainAgent verification refresh found and corrected release
    evidence drift: the current full unittest suite now runs 193 tests, not the
    earlier 192-test count.
  - 2026-05-25 pro-docs handoff-structure review separated residual
    operational checks from historical follow-up evidence so the canonical
    handoff does not imply completed dated change units are still open
    operational checks.
  - 2026-05-25 MainAgent integration review accepted two additional scoped
    change units: runtime launch-install manifest coverage and docs-contract
    peer-consultation disposition traceability.
  - SPEC sections: Minimal Runtime Responsibilities; Release Evidence And
    SPEC Traceability; Completion Criteria.
  - owner_dri/reviewers: pro-runtime implemented launch-install manifest
    coverage and reported no runtime blocker; pro-docs implemented
    docs-contract traceability and the handoff-structure correction; MainAgent
    reviewed and integrated both scoped results plus the handoff-structure
    correction.
  - affected scope: `tests/test_launch_material_install_contract.py`,
    `.github/pull_request_template.md`, `tests/test_change_control_surface.py`,
    and `Handoff.md`.
  - required checks: `python3 -m unittest discover -s tests` passed, 193 tests;
    `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-main-final
    python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks
    tests -name '*.py')` passed; scoped no-index `git diff --check` produced
    no whitespace errors for the changed generated-copy files.
  - candidate-ledger disposition: integrated; evidence:
    `tests/test_launch_material_install_contract.py`,
    `tests/test_change_control_surface.py`, `.github/pull_request_template.md`,
    `Handoff.md`, and ProfessionalAgent panes `%1296` / `%1297`; verification
    refresh evidence: MainAgent full-suite run on 2026-05-25 and review panes
    `%1306` / `%1307`, with later MainAgent evidence-refresh review using
    panes `%1311` / `%1312`, handoff-structure review using panes `%1317` /
    `%1318`, and peer-send polling-floor review using panes `%1322` / `%1323`.
  - deterministic finalization blockers: none known after MainAgent final
    sweep; generated-copy target remains untracked from the parent Git
    worktree, so no-index diff checks are used for scoped whitespace evidence.
  - blocking objections: none.
- Latest generated-copy checks after the pro-docs docs-contract pass:
  - 2026-05-25 pro-docs review found a SPEC traceability gap where PR
    change-unit evidence required reviewers but did not explicitly require the
    peer consultation disposition when applicable.
  - SPEC section: Release Evidence And SPEC Traceability.
  - owner_dri/reviewers: pro-docs implemented; pro-runtime consultation
    reported no runtime blocking objection and accepted docs-contract
    strengthening as scoped evidence.
  - affected scope: `.github/pull_request_template.md`,
    `tests/test_change_control_surface.py`, and `Handoff.md`.
  - required checks: targeted `python3 -m unittest
    tests.test_change_control_surface tests.test_spec_contract` passed;
    full `python3 -m unittest discover -s tests` passed, 188 tests;
    no-index `git diff --check` passed for the three scoped files because the
    generated-copy target is untracked from the parent Git worktree.
  - candidate-ledger disposition: integrated; evidence:
    `tests/test_change_control_surface.py`, `.github/pull_request_template.md`,
    `Handoff.md`, and ProfessionalAgent pane `%1296`.
  - deterministic finalization blockers: not evaluated for the whole run by
    pro-docs; scoped task moved to Team review.
  - blocking objections: none.
- Latest generated-copy checks after the main integration pass:
  - 2026-05-25 MainAgent integration review accepted three scoped change units:
    submit-key boundary validation, release-evidence traceability, and
    `doctor.py` extraction from `cli.py` for focused runtime responsibility.
  - SPEC sections: tmux Communication; Instruction Isolation; Hook-Driven
    Re-kick; Development Policy; Release Evidence And SPEC Traceability.
  - owner_dri/reviewers: pro-runtime implemented submit-key validation and
    resolved pro-quality request-changes; pro-quality implemented release
    evidence and accepted the runtime fix; MainAgent implemented the CLI
    responsibility split and final integration review.
  - affected scope: `.codex/agent_orchestra_minimal/{cli.py,doctor.py,
    launch_io.py,launch_material.py,prepare_agent_launch.py,tmux_delivery.py,
    tmux_wake.py}`, `tests/{test_runtime_boundaries.py,
    test_submit_key_defaults.py,test_probe_cleanup.py,
    test_change_control_surface.py}`, and `Handoff.md`.
  - required checks: `python3 -m unittest discover -s tests` passed, 187 tests;
    `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-main python3 -m
    py_compile $(find .codex/agent_orchestra_minimal .codex/hooks tests -name
    '*.py')` passed; `git -C ${AGENT_ORCHESTRA_LEGACY_ROOT} diff --check
    -- AgentOrchestra` passed; path-form Nix `nix build
    path:$PWD#checks.$(nix eval --raw --impure --expr
    builtins.currentSystem).source-contract` passed.
  - candidate-ledger disposition: integrated; evidence:
    `tests/test_submit_key_defaults.py`, `tests/test_probe_cleanup.py`,
    `tests/test_change_control_surface.py`, `tests/test_runtime_boundaries.py`,
    `Handoff.md`, and ProfessionalAgent panes `%1291` / `%1292`.
  - deterministic finalization blockers: none after MainAgent final sweep.
  - blocking objections: none; pro-quality's run_probe objection was resolved
    and accepted before integration.
- Earlier generated-copy checks after the pro-quality release-evidence pass:
  - 2026-05-25 QA/change-control review compared root `SPEC.md` with
    generated-copy release evidence, workflow gates, and change-control tests.
  - change unit: latest `Handoff.md` release evidence now records the SPEC
    traceability minimums for the current scoped improvement, and
    `tests/test_change_control_surface.py` prevents the latest evidence block
    from omitting them.
  - SPEC section: Release Evidence And SPEC Traceability.
  - owner_dri/reviewers: pro-quality implemented; Team review pending from
    MainAgent/pro-runtime as applicable.
  - affected scope: Handoff.md and tests/test_change_control_surface.py.
  - required checks: targeted `python3 -m unittest
    tests.test_change_control_surface` passed; full `python3 -m unittest
    discover -s tests` passed, 183 tests; `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-pro-quality
    python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks
    tests -name '*.py')` passed; `git diff --check -- .codex tests
    Handoff.md SPEC.md .github .gitignore flake.nix flake.lock` passed.
  - path-form Nix `nix build path:$PWD#checks.$(nix eval --raw --impure
    --expr builtins.currentSystem).source-contract` passed.
  - candidate-ledger disposition: integrated; evidence:
    `tests/test_change_control_surface.py`, `Handoff.md`.
  - deterministic finalization blockers: none for this scoped candidate.
  - blocking objections: none.
- Earlier generated-copy checks after the handoff-current-verification pass:
  - 2026-05-25 self-improvement E2E selected `pro-runtime` (Layer 16 runtime)
    and `pro-docs` (Layer 25 documentation/contracts) as the smallest
    sufficient ProfessionalAgent team for runtime/SPEC improvement.
  - change unit: `Handoff.md` now records the current latest verification first,
    and `tests/test_change_control_surface.py` prevents stale latest wording
    from returning.
  - `python3 -m unittest tests.test_change_control_surface` passed, 4 tests.
  - `python3 -m unittest discover -s tests` passed, 180 tests.
  - `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-main-214636 python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py')` passed.
  - `git diff --check -- AgentOrchestra/.codex AgentOrchestra/tests AgentOrchestra/Handoff.md AgentOrchestra/SPEC.md AgentOrchestra/.github AgentOrchestra/.gitignore AgentOrchestra/flake.nix AgentOrchestra/flake.lock` passed from the parent repo.
  - Path-form Nix `nix build path:$PWD#checks.$(nix eval --raw --impure --expr builtins.currentSystem).source-contract` passed.
  - reviewers: `pro-docs` accepted with no docs/release-evidence objection;
    `pro-runtime` requested the 180-test latest evidence correction, then
    accepted with no runtime/test-contract objection.
  - blocking objections: none after the 180-test evidence correction.
- Earlier generated-copy checks after the startup-wording pass:
  - `python3 -m unittest discover -s tests` passed, 179 tests.
  - `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-main python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py')` passed.
  - `git diff --check -- .codex tests layers Handoff.md SPEC.md .gitignore flake.nix flake.lock .github` passed.
  - Path-form Nix `nix build path:$PWD#checks.$(nix eval --raw --impure --expr builtins.currentSystem).source-contract` passed.
  - Residual candidate disposition: no in-scope runtime liveness, launch
    isolation, task-file finalization, tmux delivery, or documentation
    traceability candidate remained after Team sweep.
- Earlier root checks after accepting the candidate-ledger and fresh-wake proposal:
  - 2026-05-25 self-improvement E2E selected `pro-runtime` (Layer 16 runtime)
    and `pro-docs` (Layer 25 documentation/contracts) as the smallest
    sufficient ProfessionalAgent team for runtime/SPEC improvement.
  - `python3 -m unittest discover -s tests` passed, 168 tests.
  - `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-root python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py')` passed.
  - `git diff --check -- .codex tests layers Handoff.md SPEC.md flake.nix flake.lock .github .gitignore` passed.
  - Live agent-orchestra review evidence: `pro-runtime` integrated Stop Hook
    fresh-wake delivery hardening and accepted the fix after review;
    `pro-docs` integrated the task-file Skill `Candidates` description
    contract and accepted the fix after review; MainAgent ran final
    verification and retired ProfessionalAgent panes.
- No `E2E.md` file is present in this generated copy. Treat live tmux/Codex E2E
  as operational evidence rather than a generated-copy project record.
- Local improvement-loop files under `.codex/tmp/` are operational state, not
  runtime source. Keep them ignored in the root project and exclude `.codex/tmp/`
  when regenerating `AgentOrchestra/`.

## Remaining Operational Checks

- No in-scope AgentOrchestra improvement candidate remains from the current
  SPEC-driven pass after the 2026-05-25 MainAgent, runtime, and docs review
  cycle.
- If these generated-copy changes are later promoted into another root/runtime
  surface, reinstall `codex-o`, regenerate `AgentOrchestra/`, and run a
  follow-up E2E against that promoted surface.
- During E2E, continue watching:
  - whether messages left in a Codex TUI composer are retried or reported;
  - whether `[Candidates]` prevents premature `done`;
  - whether Pro panes are retired before MainAgent reports completion.

## Historical Follow-up Evidence

- 2026-05-25 follow-up liveness pass:
  - change unit: active ProfessionalAgent missing own pane env now wakes the
    Main pane fallback instead of returning no action;
  - owner_dri/reviewers: pro-sre-22 implemented, pro-runtime-16 peer-reviewed
    with no blocking objection, MainAgent reviewed;
  - evidence: `.codex/agent_orchestra_minimal/tmux_wake.py`,
    `tests/test_stop_hook_recovery.py`;
  - checks: targeted `python3 -m unittest tests.test_stop_hook_recovery
    tests.test_stop_hook_fallback tests.test_stop_hook_invalid_task_file` and
    targeted `py_compile` passed;
  - full-run checks: `python3 -m unittest discover -s tests` passed with 170
    tests; `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-main-full
    python3 -m py_compile $(find .codex/agent_orchestra_minimal .codex/hooks
    tests -name '*.py')` passed; `git diff --check -- AgentOrchestra/.codex
    AgentOrchestra/tests AgentOrchestra/Handoff.md AgentOrchestra/SPEC.md
    AgentOrchestra/.github AgentOrchestra/.gitignore AgentOrchestra/flake.nix
    AgentOrchestra/flake.lock` passed from the parent repo; `nix build
    path:$PWD#checks.$(nix eval --raw --impure --expr
    builtins.currentSystem).source-contract` passed from `AgentOrchestra/`;
  - note: plain `nix build .#checks...` failed because the parent Git repo does
    not track `AgentOrchestra/flake.nix`, so path-form Nix was required for the
    generated copy.
- 2026-05-25 generated-startup wording pass:
  - change unit: generated ProfessionalAgent startup behavior now describes
    launch as generated isolated `AGENTS.md` behavior plus selected layer
    perspective, avoiding wording that can imply layer instructions are the
    startup behavior source;
  - owner_dri/reviewers: pro-docs-25 implemented, pro-runtime-16
    cross-checked runtime boundaries and reported no runtime-code change
    required, MainAgent reviewed;
  - evidence: `.codex/agent_orchestra_minimal/agent_templates/common.AGENTS.md`,
    `tests/test_launch_material_contract.py`,
    `tests/test_runtime_boundaries.py`;
  - checks: targeted `python3 -m unittest
    tests.test_launch_material_contract tests.test_runtime_boundaries` passed;
    full `python3 -m unittest discover -s tests` passed with 179 tests;
    `PYTHONPYCACHEPREFIX=/private/tmp/agent-orchestra-pycache-main python3 -m
    py_compile $(find .codex/agent_orchestra_minimal .codex/hooks tests -name
    '*.py')` passed; `git diff --check -- .codex tests layers Handoff.md
    SPEC.md .gitignore flake.nix flake.lock .github` passed; path-form Nix
    `nix build path:$PWD#checks.$(nix eval --raw --impure --expr
    builtins.currentSystem).source-contract` passed;
  - residual candidate disposition: no in-scope runtime liveness, launch
    isolation, task-file finalization, tmux delivery, or documentation
    traceability candidate remained after Team sweep.
