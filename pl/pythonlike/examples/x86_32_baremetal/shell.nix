with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "demo-baremetal";
  buildInputs = [
    python311
    gnumake
    grub2
    xorriso
    pkgsCross.i686-embedded.buildPackages.gcc
  ];
}
