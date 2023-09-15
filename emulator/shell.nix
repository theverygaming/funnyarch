with import <nixpkgs> { };
let
  gccForLibs = stdenv.cc.cc;
in
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    SDL2

    python311
  ];
}
