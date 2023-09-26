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
    icestorm
    nextpnr

    SDL2

    python311
  ];
}
