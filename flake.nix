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
        in
        {
          default = codex-o;
          agent-orchestra = agent-orchestra-cli;
          codex-o = codex-o;
        }
      );

      checks = forAllSystems (
        { pkgs, ... }:
        {
          source-contract = pkgs.runCommand "agent-orchestra-source-contract-tests" { nativeBuildInputs = [ pkgs.python3 ]; } ''
            cp -R ${self} source
            chmod -R u+w source
            cd source
            python3 -m py_compile .codex/agent_orchestra_minimal/*.py .codex/hooks/*.py tests/*.py
            python3 -m unittest discover -s tests
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
            meta.description = "Run the agent-orchestra CLI";
          };
          codex-o = {
            type = "app";
            program = "${self.packages.${system}.codex-o}/bin/codex-o";
            meta.description = "Start agent-orchestra MainAgent with codex-o";
          };
        }
      );
    };
}
