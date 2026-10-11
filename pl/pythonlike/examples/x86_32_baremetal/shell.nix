with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "demo-baremetal";
  buildInputs = [
    python313
    gnumake
    grub2
    xorriso
    pkgsCross.i686-embedded.buildPackages.gcc
    qemu
  ];
}
