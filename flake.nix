{
  description = "Nix-wrapped pipewire scripts";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # A mapping from script names (without .sh) to their dependencies.
        scriptDeps = {
          find_by_media_name = [ pkgs.pipewire pkgs.jq ];
          find_by_node_desc = [ pkgs.pipewire pkgs.jq ];
          find_by_node_desc_capture_group = [ pkgs.pipewire pkgs.jq ];
          monitor = [ pkgs.ffmpeg ];
          toggle_mute = [ pkgs.pipewire pkgs.coreutils pkgs.gnugrep ];
          virtual = [ pkgs.pipewire pkgs.pulseaudio ];
          sum_flacs = [ pkgs.python3 pkgs.ffmpeg ];
        };

        shellScripts = builtins.mapAttrs (name: deps:
          if name == "sum_flacs" then
            pkgs.writeScriptBin name ''
              #!${pkgs.python3}/bin/python3
              ${builtins.readFile ./scripts/${name}.py}
            ''
          else
            pkgs.writeShellApplication {
              inherit name;
              runtimeInputs = deps;
              text = builtins.readFile ./scripts/${name}.sh;
            }
        ) scriptDeps;

      in
      {
        packages = shellScripts;

        defaultPackage = self.packages.${system}.toggle_mute;
      }
    );
}
