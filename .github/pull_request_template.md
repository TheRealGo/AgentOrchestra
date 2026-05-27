## AgentOrchestra Change Control

- [ ] For AgentOrchestra runtime or instruction changes, `python3 -m unittest discover -s tests` passes.
- [ ] For AgentOrchestra runtime Python changes, `python3 -m py_compile` passes for the affected runtime surfaces.
- [ ] For AgentOrchestra runtime, instruction, or contributor-doc changes, `git diff --check -- .codex tests layers Handoff.md README.md README.ja.md SPEC.md .gitignore flake.nix flake.lock .github` passes.
- [ ] For AgentOrchestra runtime or instruction changes, `nix flake check --no-build` passes from the repository root, or the exception is documented.
- [ ] For AgentOrchestra runtime or instruction changes, `nix build .#checks.x86_64-linux.source-contract` passes, or the exception is documented.
- [ ] For generated-copy or untracked-fixture verification, path-form Nix checks pass, for example `nix flake check --no-build path:$PWD` and `nix build path:$PWD#checks.$system.source-contract`, or the exception is documented.
- [ ] `SPEC.md` and runtime evidence are updated when runtime behavior, Hook behavior, or tmux lifecycle behavior changes.
- [ ] Change-unit evidence is recorded: `owner_dri`, affected scope, reviewers, peer consultation disposition when applicable, required checks, blocking objections, and resolution/evidence.
- [ ] ProfessionalAgent sufficiency is recorded: selected layers, skipped layers or SubAgents, and evidence needs.
- [ ] Final improvement-candidate sweep evidence is recorded: ProfessionalAgent recommendations, skipped verification, E2E observations, and operational issues are integrated, rejected, deferred, blocked, out-of-scope, marked `needs_user`, or added to `[Backlog]`.
- [ ] Shared task file finalization evidence is recorded: `[status] done` only after `[Backlog]`, `[InProgress]`, and `[InReview]` are empty, every `[Candidates]` item has a completed disposition, and the deterministic finalization blocker list is empty or explicitly dispositioned.
- [ ] SPEC traceability is recorded: affected SPEC section, `owner_dri`, affected scope, reviewers, required checks, candidate-ledger disposition, blocking objections, and resolution/evidence.
- [ ] ProfessionalAgent retirement evidence is recorded: accepted result, `/exit` attempt, pane verification, and `kill-pane` cleanup when needed.
- [ ] Any unresolved live tmux/Codex E2E gap is explicitly recorded as a residual risk.
