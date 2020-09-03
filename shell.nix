{ pkgs ? import <nixpkgs> {} }:
with pkgs;
mkShell {
  VENV = "env";
  buildInputs = [
    git
    python38Full
    python38Packages.conda
    python38Packages.tox
    stdenv
    libpqxx
    zlib
    zlib.dev
    libffi
    libffi.dev
    travis
    stdenv.cc.cc.lib
    pam
  ];
  shellHook = ''
    export PYTHONPATH=`pwd`/$VENV/${python.sitePackages}:$PYTHONPATH;
    export LD_LIBRARY_PATH="${stdenv.cc.cc.lib}/lib64:$LD_LIBRARY_PATH";
  '';
}
