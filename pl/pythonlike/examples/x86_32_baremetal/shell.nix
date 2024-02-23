with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "demo-baremetal";
  buildInputs = [
    python311
    gnumake
    pkgsCross.i686-embedded.buildPackages.gcc
  ];
}
