{
  description = "agent-orchestra minimal runtime";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "aarch64-darwin"
        "x86_64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];

      forAllSystems =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f {
            inherit system;
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      packages = forAllSystems (
        { pkgs, ... }:
        let
          agent-orchestra-cli = pkgs.writeShellApplication {
            name = "agent-orchestra";
            runtimeInputs = [
              pkgs.python3
              pkgs.tmux
            ];
            text = ''
              export AGENT_ORCHESTRA_REPO_ROOT="${self}"
              exec ${pkgs.python3}/bin/python3 "${self}/.codex/agent_orchestra_minimal/cli.py" "$@"
            '';
          };
          codex-o = pkgs.writeShellApplication {
            name = "codex-o";
            runtimeInputs = [
              pkgs.python3
              pkgs.tmux
            ];
            text = ''
              export AGENT_ORCHESTRA_REPO_ROOT="${self}"
              exec ${pkgs.python3}/bin/python3 "${self}/.codex/agent_orchestra_minimal/cli.py" start "$@"
            '';
          };
          agent-orchestra-claude-cli = pkgs.writeShellApplication {
            name = "agent-orchestra-claude";
            runtimeInputs = [
              pkgs.python3
              pkgs.tmux
            ];
            text = ''
              export AGENT_ORCHESTRA_REPO_ROOT="${self}"
              exec ${pkgs.python3}/bin/python3 "${self}/.claude/agent_orchestra_minimal/cli.py" "$@"
            '';
          };
          claude-o = pkgs.writeShellApplication {
            name = "claude-o";
            runtimeInputs = [
              pkgs.python3
              pkgs.tmux
            ];
            text = ''
              export AGENT_ORCHESTRA_REPO_ROOT="${self}"
              exec ${pkgs.python3}/bin/python3 "${self}/.claude/agent_orchestra_minimal/cli.py" start "$@"
            '';
          };
        in
        {
          default = codex-o;
          agent-orchestra = agent-orchestra-cli;
          codex-o = codex-o;
          agent-orchestra-claude = agent-orchestra-claude-cli;
          claude-o = claude-o;
        }
      );

      checks = forAllSystems (
        { pkgs, ... }:
        {
          source-contract = pkgs.runCommand "agent-orchestra-source-contract-tests" { nativeBuildInputs = [ pkgs.python3 pkgs.git ]; } ''
            cp -R ${self} source
            chmod -R u+w source
            cd source
            find .codex/agent_orchestra_minimal .codex/hooks tests -name '*.py' -print0 | xargs -0 python3 -m py_compile
            python3 -m unittest discover -s tests
            touch "$out"
          '';
          claude-source-contract = pkgs.runCommand "agent-orchestra-claude-source-contract-tests" { nativeBuildInputs = [ pkgs.python3 ]; } ''
            cp -R ${self} source
            chmod -R u+w source
            cd source
            find .claude/agent_orchestra_minimal .claude/hooks tests_claude -name '*.py' -print0 | xargs -0 python3 -m py_compile
            python3 -m unittest discover -s tests_claude
            touch "$out"
          '';
        }
      );

      devShells = forAllSystems (
        { pkgs, ... }:
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.python3
              pkgs.tmux
            ];
          };
        }
      );

      apps = forAllSystems (
        { system, ... }:
        {
          default = {
            type = "app";
            program = "${self.packages.${system}.default}/bin/codex-o";
            meta.description = "Start agent-orchestra MainAgent with codex-o";
          };
          agent-orchestra = {
            type = "app";
            program = "${self.packages.${system}.agent-orchestra}/bin/agent-orchestra";
            meta.description = "Run the agent-orchestra CLI (Codex)";
          };
          codex-o = {
            type = "app";
            program = "${self.packages.${system}.codex-o}/bin/codex-o";
            meta.description = "Start agent-orchestra MainAgent with codex-o";
          };
          agent-orchestra-claude = {
            type = "app";
            program = "${self.packages.${system}.agent-orchestra-claude}/bin/agent-orchestra-claude";
            meta.description = "Run the agent-orchestra CLI (Claude Code)";
          };
          claude-o = {
            type = "app";
            program = "${self.packages.${system}.claude-o}/bin/claude-o";
            meta.description = "Start agent-orchestra MainAgent with claude-o";
          };
        }
      );
    };
}
