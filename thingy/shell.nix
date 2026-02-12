with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    python313
    python313Packages.lark
    gcc
  ];
}
