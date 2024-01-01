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
  ];
  shellHook = ''
    EM_CACHE=~/.emscripten_cache
  '';
}
