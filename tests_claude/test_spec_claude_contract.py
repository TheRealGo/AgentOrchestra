from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SpecClaudeContractTests(unittest.TestCase):
    def test_flake_adds_claude_launcher_without_overriding_user_cli(self) -> None:
        flake = (ROOT / "flake.nix").read_text(encoding="utf-8")

        for phrase in (
            'name = "claude-o"',
            "claude-o = claude-o;",
            '"${self}/.claude/agent_orchestra_minimal/cli.py" start "$@"',
            'program = "${self.packages.${system}.claude-o}/bin/claude-o"',
            "Start agent-orchestra MainAgent with claude-o",
        ):
            self.assertIn(phrase, flake)

        # The Codex launcher coexists (両対応): claude-o is added, codex-o stays.
        self.assertIn("codex-o = codex-o;", flake)
        self.assertIn('program = "${self.packages.${system}.codex-o}/bin/codex-o"', flake)

        # The runtime relies on the user's own Claude Code CLI; the flake must not
        # vendor a `claude` (or `codex`) package.
        self.assertIn("pkgs.python3", flake)
        self.assertIn("pkgs.tmux", flake)
        self.assertNotIn("pkgs.claude", flake)
        self.assertNotIn("pkgs.codex", flake)

        for system in ("aarch64-darwin", "x86_64-darwin", "aarch64-linux", "x86_64-linux"):
            self.assertIn(f'"{system}"', flake)

    def test_flake_exposes_claude_source_contract_check(self) -> None:
        flake = (ROOT / "flake.nix").read_text(encoding="utf-8")

        for phrase in (
            'claude-source-contract = pkgs.runCommand "agent-orchestra-claude-source-contract-tests"',
            "nativeBuildInputs = [ pkgs.python3 ];",
            "find .claude/agent_orchestra_minimal .claude/hooks tests_claude -name '*.py' -print0",
            "xargs -0 python3 -m py_compile",
            "python3 -m unittest discover -s tests_claude",
        ):
            self.assertIn(phrase, flake)

        # The Codex source-contract check is unchanged and coexists.
        self.assertIn('source-contract = pkgs.runCommand "agent-orchestra-source-contract-tests"', flake)
        self.assertIn("find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0", flake)
        self.assertIn("python3 -m unittest discover -s tests", flake)

    def test_spec_claude_defines_claude_launch_argv(self) -> None:
        spec = (ROOT / "SPEC.claude.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())

        self.assertIn('claude --add-dir "$TARGET_PROJECT" --add-dir "$RUN_DIR" --permission-mode "$MODE"', spec)
        # The run dir is added as a second --add-dir for the shared task/state files.
        self.assertIn("run directory is added as a second `--add-dir`", spec_normalized)
        self.assertIn("`$MODE` defaults to `bypassPermissions`", spec_normalized)
        # bypassPermissions is the default; its one-time launch gate is accepted at launch.
        self.assertIn("Bypass Permissions warning gate", spec_normalized)
        self.assertIn("AGENT_ORCHESTRA_PERMISSION_MODE", spec)
        self.assertIn("never `--cd`", spec_normalized)
        self.assertIn("no `--cd` flag", spec_normalized)
        self.assertIn("synthetic first prompt is forbidden", spec_normalized)
        # Allowed extra args must be enumerated.
        for allowed in ("--model", "--fallback-model", "--verbose"):
            self.assertIn(allowed, spec_normalized)
        # Boundary options that must not be overridden.
        for option in (
            "--add-dir",
            "--permission-mode",
            "--settings",
            "--setting-sources",
            "--dangerously-skip-permissions",
            "--allow-dangerously-skip-permissions",
            "--system-prompt",
            "--append-system-prompt",
            "--agents",
            "-p`/`--print",
        ):
            self.assertIn(option, spec_normalized)

    def test_spec_claude_defines_settings_and_trust_seed(self) -> None:
        spec = (ROOT / "SPEC.claude.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())

        self.assertIn("settings.json", spec)
        self.assertIn("no per-hash hook trust model", spec_normalized)
        self.assertIn("no trusted-hash field", spec_normalized)
        # bypassPermissions is the default because no scoped allow-list covers
        # arbitrary repo paths (incl. dot-dirs); the settings carry only the mode,
        # and the looser-than-Codex (no sandbox) posture is documented honestly.
        self.assertIn('"permissions": { "defaultMode": "bypassPermissions" }', spec)
        self.assertIn("path-glob allow rule (`Edit(//target/**)`) was verified to miss dot-directories", spec_normalized)
        self.assertIn("looser than the Codex posture", spec_normalized)
        self.assertIn("absolute, shell-quoted path", spec_normalized)
        self.assertIn("Is this a project you created", spec)
        self.assertIn(".claude.json", spec)
        self.assertIn("hasTrustDialogAccepted", spec)
        self.assertIn("CLAUDE.md", spec)

    def test_spec_claude_documents_macos_keychain_auth_prerequisite(self) -> None:
        spec = (ROOT / "SPEC.claude.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())

        self.assertIn("## Authentication", spec)
        self.assertIn("Keychain", spec)
        self.assertIn(".credentials.json", spec)
        self.assertIn("ANTHROPIC_API_KEY", spec)
        self.assertIn("must not extract Keychain secrets", spec_normalized)
        self.assertIn("deployment prerequisite, not a runtime defect", spec_normalized)
        # The empirically verified fact must stay documented: an isolated config
        # does not consult the Keychain, and seeding oauthAccount does not change that.
        self.assertIn("does not read them", spec_normalized)
        self.assertIn("seeding the account does not", spec_normalized)
        # The runtime forwards a single exported credential to every Agent.
        self.assertIn("CLAUDE_CODE_OAUTH_TOKEN", spec)
        self.assertIn("forwards the auth", spec_normalized)
        self.assertIn("env.sh", spec)
        # Auth is required (Agents are non-functional without it) and scales via
        # the forwarded env.sh, not a per-Agent `/login` that only authenticates
        # the single isolated config it runs in.
        self.assertIn("cannot do any work without a credential", spec_normalized)
        self.assertIn("does not propagate to the other Agents", spec_normalized)

    def test_spec_claude_defines_tui_markers_and_fire_and_forget_wake(self) -> None:
        spec = (ROOT / "SPEC.claude.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())

        self.assertIn("❯", spec)
        self.assertIn("begin with `⏺`", spec_normalized)
        self.assertIn("rotating spinner glyph", spec_normalized)
        self.assertIn("esc to interrupt", spec)
        self.assertIn("`pane_title` containing `Claude Code`", spec_normalized)
        self.assertIn("`pane_current_command` is unreliable", spec_normalized)

        self.assertIn("fire-and-forget", spec_normalized)
        self.assertIn("`load-buffer` + `paste-buffer`", spec_normalized)
        self.assertIn("several submit-key presses", spec_normalized)
        for line in ("runtime_wake", "source=hook", "user_instruction=false"):
            self.assertIn(line, spec)
        # Honest posture: the reasonless payload + candidate ledger are
        # byte-identical to Codex, so a near-miss disposition can re-kick without
        # converging; the Claude port recovers convergence in the guidance layer
        # (skill + templates), not by diverging the shared deterministic core.
        self.assertIn("byte-identical to the Codex runtime", spec_normalized)
        self.assertIn("re-kicks forever while the woken agent reports", spec_normalized)
        self.assertIn("recovers convergence in the runtime-specific guidance layer", spec_normalized)

    def test_spec_claude_maps_codex_concepts_to_claude(self) -> None:
        spec = (ROOT / "SPEC.claude.md").read_text(encoding="utf-8")

        for phrase in (
            "`CODEX_HOME` | `CLAUDE_CONFIG_DIR`",
            "generated `workspace/CLAUDE.md`",
            "Claude Code subagent (Task/Agent tool, `.claude/agents`)",
            "`claude -p` / `--print`",
        ):
            self.assertIn(phrase, spec)

    def test_spec_claude_uses_tests_claude_verification(self) -> None:
        spec = (ROOT / "SPEC.claude.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())

        self.assertIn("discover -s tests_claude", spec_normalized)
        self.assertIn("claude-source-contract", spec_normalized)


if __name__ == "__main__":
    unittest.main()
