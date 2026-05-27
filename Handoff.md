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
    '*.py')` passed; `git -C /Users/therealgo/Codex/INSTRUCTIONS diff --check
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
