{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs.buildPackages; [ python3 python3Packages.markdown python3Packages.pymdown-extensions python3Packages.python-lsp-server ];
}
