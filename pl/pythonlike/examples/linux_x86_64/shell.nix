with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "demo";
  buildInputs = [
    python313
    gnumake
    gcc
  ];
}
