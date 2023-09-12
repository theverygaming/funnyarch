with import <nixpkgs> { };
let
  gccForLibs = stdenv.cc.cc;
in
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    verilator
    gtkwave
    yosys

    python311
  ];
}
