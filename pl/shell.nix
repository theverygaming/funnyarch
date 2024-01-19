with import <nixpkgs> { };
let
in
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    python311
  ];
}
