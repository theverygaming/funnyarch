with import <nixpkgs> { };
let
in
stdenv.mkDerivation {
  name = "funnyarch-assembler";
  buildInputs = [
    python313
  ];
}
