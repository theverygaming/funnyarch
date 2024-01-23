with import <nixpkgs> { };
let
  gccForLibs = stdenv.cc.cc;
in
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    SDL2

    #emscripten

    python311
    #python311Packages.wand
    #(python311Packages.opencv4.override { enableGtk2 = true; })
  ];
  shellHook = ''
    export EM_CACHE=~/.emscripten_cache
  '';
}
