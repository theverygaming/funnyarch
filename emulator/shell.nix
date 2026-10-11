with import <nixpkgs> { };
stdenv.mkDerivation {
  name = "funnyarch";
  buildInputs = [
    SDL2

    #emscripten

    python313
    #python313Packages.wand
    #(python313Packages.opencv4.override { enableGtk3 = true; })
  ];
  shellHook = ''
    export EM_CACHE=~/.emscripten_cache
  '';
}
