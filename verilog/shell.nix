with import <nixpkgs> { };
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
