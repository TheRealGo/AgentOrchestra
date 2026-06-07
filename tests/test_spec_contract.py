from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SpecContractTests(unittest.TestCase):
    def test_package_does_not_override_user_codex_cli(self) -> None:
        flake = (ROOT / "flake.nix").read_text(encoding="utf-8")
        self.assertIn("pkgs.python3", flake)
        self.assertIn("pkgs.tmux", flake)
        self.assertNotIn("pkgs.codex", flake)

    def test_flake_exposes_minimal_agent_orchestra_package_and_app(self) -> None:
        flake = (ROOT / "flake.nix").read_text(encoding="utf-8")

        required_phrases = [
            'description = "agent-orchestra minimal runtime"',
            'name = "agent-orchestra"',
            'name = "codex-o"',
            "writeShellApplication",
            'export AGENT_ORCHESTRA_REPO_ROOT="${self}"',
            '"${self}/.codex/agent_orchestra_minimal/cli.py"',
            'cli.py" start "$@"',
            "default = codex-o",
            "agent-orchestra = agent-orchestra-cli",
            "codex-o = codex-o",
            'type = "app"',
            'program = "${self.packages.${system}.default}/bin/codex-o"',
            'program = "${self.packages.${system}.agent-orchestra}/bin/agent-orchestra"',
            'program = "${self.packages.${system}.codex-o}/bin/codex-o"',
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, flake)

        for system in ("aarch64-darwin", "x86_64-darwin", "aarch64-linux", "x86_64-linux"):
            self.assertIn(f'"{system}"', flake)

        self.assertNotIn("mkDerivation", flake)
        self.assertNotIn("makeWrapper", flake)

    def test_flake_exposes_source_contract_check_for_ci_verification(self) -> None:
        flake = (ROOT / "flake.nix").read_text(encoding="utf-8")

        required_phrases = [
            "checks = forAllSystems",
            'source-contract = pkgs.runCommand "agent-orchestra-source-contract-tests"',
            "nativeBuildInputs = [ pkgs.python3 pkgs.git ];",
            "find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0",
            "xargs -0 python3 -m py_compile",
            "python3 -m unittest discover -s tests",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, flake)

    def test_flake_exposes_default_development_shell(self) -> None:
        flake = (ROOT / "flake.nix").read_text(encoding="utf-8")

        for phrase in ("devShells = forAllSystems", "default = pkgs.mkShell", "pkgs.python3", "pkgs.tmux"):
            self.assertIn(phrase, flake)

    def test_spec_defines_minimal_runtime_boundaries(self) -> None:
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())

        required_phrases = [
            "MainAgent and ProfessionalAgents start without context contamination",
            "tmux panes are the primary Agent communication channel",
            "AGENT_ORCHESTRA_TUI_SUBMIT_KEY",
            "defaulting to `C-m`",
            "Runtime must not own ProfessionalAgent pane scheduling",
            "Every run has a single shared task file",
            "Each required section must appear exactly once",
            "Duplicate or unknown sections are invalid",
            "If the task file is missing, unreadable, or invalid",
            "Agent stopping is detected by Codex official Hooks",
            "Runtime owns only deterministic rails",
            "Runtime must not own",
            "`--cd` points at the isolated workspace",
            "`--add-dir` grants access to the target project",
            "a detected parent Git worktree root is an additional editable/access root",
            "`--profile agent-orchestra` loads the minimal Hook/project-trust config",
            "legacy or user-supplied profile flags such as `--profile-v2`",
            "must be rejected from extra Codex args",
            "approval policy, sandbox mode, hooks enablement, and network access",
            "if `codex features list` reports `prevent_idle_sleep`",
            "AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP=1",
            "repository startup instruction surface is controlled by generated",
            "must not inject a synthetic first user prompt",
            "must not treat `--` or trailing argv as an initial task",
            "must not live under the target project tree",
            "provide env/argv metadata",
            "Skills should be split by operation surface",
            "Do not collapse these back into one large tmux Skill",
            "concrete send/capture/retry procedure belongs in the tmux Skills",
            "must not silently treat unconfirmed communication as delivered",
            "`codex exec` ProfessionalAgents",
            "ProfessionalAgent protocol layers resolve from",
            "AGENT_ORCHESTRA_REPO_ROOT/layers",
            "never from the target project's",
            "preserves `AGENT_ORCHESTRA_REPO_ROOT` in both `env.json` and",
            "hard limit is 300 lines per file",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, spec_normalized)

    def test_spec_defines_agent_orchestra_operating_identity(self) -> None:
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")

        required_phrases = [
            "このプロジェクトは、複数の独立したAgentが",
            "MainAgentが複数のProfessionalAgentを独立環境で立ち上げる",
            "MainAgentは唯一のユーザー-facing Agentであり、AgentTeamのstewardです",
            "ProfessionalAgentは独立したCodex CLI sessionとして立ち上がる専門Agentです",
            "編集・提案・レビュー・差し戻し・blocking objectionはAgentTeam共通の権限です",
            "SubAgentはProfessionalAgentの代替ではない",
            "Runtime側は判断しません",
            "tmux上のCodex CLI paneです",
            "global / parent / target root AGENTS.md はstartup instructionとしてloadされない",
            "判断はAgentTeamが行い、task fileは状態を表すだけ",
            "Agentic組織的開発フレームワークです",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, spec)

    def test_spec_operating_identity_matches_generated_agent_contract_rails(self) -> None:
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())

        required_phrases = [
            "role-specific startup `AGENTS.md` を生成する",
            "layer `INSTRUCTIONS.md` を専門観点としてstartup `AGENTS.md`へ添付する",
            "Codex CLI の `--cd` / `--add-dir` / `--profile`",
            "ProfessionalAgent同士の直接相談は通常の協働経路",
            "tmux通信の具体手順はSkillが担う",
            "配送確認できない通信を成功扱いしない",
            "ProfessionalAgentは自分のlayer観点から起動される",
            "Candidatesは最終改善候補ledger",
            "InReviewはMainAgent待ち専用ではなく",
            "owner_dri、affected scope、reviewers、required checks",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, spec_normalized)

        self.assertNotIn("layer-specific AGENTS.md を生成する", spec)
        self.assertNotIn("ProfessionalAgentは自分のlayer指示から起動される", spec)
        self.assertNotIn("layer固有の指示で起動する", spec)

    def test_shared_task_file_shape_is_specified(self) -> None:
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        spec_normalized = " ".join(spec.split())
        for section in ("[status]", "[Backlog]", "[InProgress]", "[InReview]", "[Candidates]", "[Done]"):
            self.assertIn(section, spec)

        self.assertIn("`[status]` allowed values:", spec)
        self.assertIn("- `progress`", spec)
        self.assertIn("- `done`", spec)
        self.assertIn("Candidate items must record an id, disposition, summary, and evidence pointer.", spec)
        self.assertIn("Candidate ids must be unique", spec)
        self.assertIn("Candidate field keys must not be duplicated", spec)
        self.assertIn("or lacks the required id, summary, or evidence pointer.", spec_normalized)
        self.assertIn("initialized empty task file is the quiet baseline", spec)
        self.assertIn("set `[status] = progress` before substantial investigation", spec_normalized)
        self.assertIn(
            "Completed dispositions are `integrated`, `rejected`, `deferred`, `blocked`",
            spec_normalized,
        )
        self.assertIn("missing, `open`, `backlog`, or unrecognized", spec_normalized)

    def test_spec_requires_team_sufficiency_not_blanket_launching(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        required_phrases = [
            "team operating model",
            "smallest team that is sufficient",
            "solo execution is acceptable for narrow, mechanical, low-risk work",
            "independent ProfessionalAgents are expected for broad, open-ended",
            "clear file edit scope",
            "not enough to bypass team",
            "not a blanket \"always launch ProfessionalAgents\" rule",
            "whole-run coordinator",
            "AgentTeam steward",
            "Equal Editing And Change Units",
            "Integration readiness is not a unilateral MainAgent permission grant",
            "set or update `/goal`",
            "mirror the current user request",
            "not a generic \"improve forever\" instruction",
            "three completed cycles",
            "Finishing one improvement cycle is `cycle_done`",
            "Continuous goals do not expand user constraints or editable surfaces",
            "record it as an out-of-scope improvement",
            "rather than from a fixed default roster",
            "ProfessionalAgent retirement is complete only after pane cleanup",
            "must not treat a state write to `retired` as enough by itself",
            "user explicitly instructs MainAgent to leave the orchestra with `/exit`",
            "tmux Main Skill self-exit procedure as its final tool action",
            "report an explicit self-exit failure",
            "The standard Python verification runner is `unittest`, not `pytest`",
            "`pytest` is not a project dependency",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, spec)

    def test_spec_requires_proactive_subagent_use_when_useful(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        required_phrases = [
            "MainAgent should use Codex-native SubAgents proactively",
            "If MainAgent avoids SubAgents on non-trivial work",
            "proactive Codex-native SubAgent use inside its own session",
            "MainAgent and ProfessionalAgents should use them aggressively",
            "owning Agent's accountability for the final output",
            "normally use at least one SubAgent",
            "SubAgent opportunity check",
            "skipping SubAgents silently",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, spec)

    def test_spec_separates_release_skill_from_minimal_runtime_launch_contract(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        self.assertIn("project-local runtime Skills required for Agent operation", spec)
        self.assertIn("### Release Skill", spec)
        self.assertIn("repository-local operator guidance for explicit release tasks", spec)
        self.assertIn("not part of the minimal runtime launch contract by default", spec)
        self.assertIn("does not make runtime responsible for release judgment", spec)

    def test_professional_agent_ready_for_review_keeps_task_in_review(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        for phrase in (
            "records `ready_for_review` before or as it reports",
            "records the scoped task in `[InReview]` rather than `[Done]`",
            "until the accepted disposition is known",
        ):
            self.assertIn(phrase, spec)

    def test_completion_criteria_include_current_runtime_gates(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        required_phrases = [
            "selected layer perspective",
            "Skill-defined tmux delivery procedures without false-accepting queued composer text or interrupting a peer pane that is still working",
            "record consultation evidence",
            "completed `[Candidates]` dispositions",
            "accepted ProfessionalAgents are marked `retired`, sent `/exit`",
            "pane cleanup verified before MainAgent reports completion",
            "user-requested MainAgent self-exit uses the tmux Main Skill self-exit procedure",
            "reports explicit failure if it cannot submit `/exit`",
            "verification uses `unittest`, direct Python `py_compile`, `git diff --check`",
            "path-form Nix checks",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, spec)

    def test_spec_requires_release_evidence_and_traceability(self) -> None:
        spec = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())

        required_phrases = [
            "Release Evidence And SPEC Traceability",
            "maps each change unit back to this SPEC and to executable verification",
            "SPEC clause or section affected",
            "owner_dri and affected scope",
            "reviewers and peer consultation disposition when applicable",
            "required checks run, skipped, or deferred with reason",
            "candidate-ledger disposition for residual improvements",
            "blocking objections and resolution evidence",
            "deterministic finalization blockers",
            "non-`done` status",
            "open work in `[Backlog]`, `[InProgress]`, or `[InReview]`",
            "unresolved `[Candidates]` entries",
            "blocker list as empty",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, spec)

if __name__ == "__main__":
    unittest.main()
