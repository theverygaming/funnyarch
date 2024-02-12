with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "demo";
  buildInputs = [
    python311
    gnumake
    gcc
  ];
}
