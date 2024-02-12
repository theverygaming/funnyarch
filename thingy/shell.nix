with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    python311
    gcc
  ];
}
