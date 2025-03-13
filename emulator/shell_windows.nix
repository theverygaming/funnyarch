with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    pkgsCross.mingwW64.buildPackages.gcc
    pkgsCross.mingwW64.SDL2
    pkgsCross.mingwW64.libgcc
    wineWow64Packages.full
  ];
  shellHook = ''
    export SDL2_DLL="${pkgsCross.mingwW64.SDL2}/bin/SDL2.dll"
    export LIBGCC_DLL="${pkgsCross.mingwW64.libgcc}"
    export STDCXX_DLL="${pkgsCross.mingwW64.buildPackages.gcc}"
  '';
}
