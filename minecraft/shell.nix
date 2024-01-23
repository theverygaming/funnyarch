{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [
    jdk17
    gradle
    libglvnd
    (vscode-with-extensions.override {
    vscodeExtensions = with vscode-extensions; [
      vscjava.vscode-gradle
      vscjava.vscode-java-debug
      redhat.java
    ];
    })
  ];
  shellHook = ''
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.buildPackages.libglvnd}/lib
  '';
}
