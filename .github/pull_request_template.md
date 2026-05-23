## AgentOrchestra Change Control

- [ ] For AgentOrchestra runtime or instruction changes, `python3 -m unittest discover -s tests` passes.
- [ ] For AgentOrchestra runtime or instruction changes, `nix flake check --no-build` passes from the repository root, or the exception is documented.
- [ ] For AgentOrchestra runtime or instruction changes, `nix build .#checks.x86_64-linux.source-contract` passes, or the exception is documented.
- [ ] `SPEC.md` and runtime evidence are updated when runtime behavior, Hook behavior, or tmux lifecycle behavior changes.
- [ ] ProfessionalAgent sufficiency is recorded: selected layers, skipped layers or SubAgents, and evidence needs.
- [ ] Shared task file finalization evidence is recorded: `[status] done` only after `[Backlog]`, `[InProgress]`, and `[InReview]` are empty.
- [ ] ProfessionalAgent retirement evidence is recorded: accepted result, `/exit` attempt, pane verification, and `kill-pane` cleanup when needed.
- [ ] Any unresolved live tmux/Codex E2E gap is explicitly recorded as a residual risk.
