{
  description = "funnyarch";

  inputs = {
    nixpkgs.url = "nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    { }
    // flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      rec {
        packages.toolchain = pkgs.stdenv.mkDerivation rec {
          name = "funnyarch-tools";

          src = ./assembler/python;

          buildInputs = [
            pkgs.python314
          ];

          installPhase = ''
            mkdir -p "$out/bin"
            cp -r lib*.py "$out/bin"
            cp -r preprocessor.py "$out/bin/preprocessor.py"
            cp -r assembler.py "$out/bin/funnyarch-none-none-as"
            cp -r linker.py "$out/bin/funnyarch-none-none-ld"
          '';
        };
        packages.rom = pkgs.stdenv.mkDerivation rec {
          name = "funnyarch-rom";

          src = ./asm;

          buildInputs = [
            packages.toolchain
          ];

          buildPhase = ''
            funnyarch-none-none-as rom/main.asm -o rom.o
            funnyarch-none-none-ld --origin 0 -o rom.bin rom.o
          '';

          installPhase = ''
            cp rom.bin "$out"
          '';
        };
        packages.emulator = pkgs.stdenv.mkDerivation rec {
          name = "funnyarch-emulator";

          src = ./emulator;

          buildInputs = [
            pkgs.SDL2
            pkgs.libx11
          ];

          installPhase = ''
            mkdir -p "$out/bin"
            cp emu "$out/bin"/funnyarch-emulator
          '';
        };
        packages.gcc = pkgs.stdenv.mkDerivation rec {
          name = "gcc-funnyarch-none-none";

          src = pkgs.fetchFromGitHub {
            owner = "theverygaming";
            repo = "gcc";
            rev = "a5dd521f68b585780dfb30113fb586f6c7254edd";
            sha256 = "sha256-3hhgiFOEVcw8bE8D2SgnSBWFnY4naIwyc3IJ+hN6t7k=";
          };

          # somehow breaks our config.sub modifications???
          updateAutotoolsGnuConfigScriptsPhase = "true";

          buildInputs = [
            pkgs.gmp
            pkgs.mpfr
            pkgs.libmpc
            pkgs.flex
            pkgs.bison
          ];

          hardeningDisable = [ "format" ];

          # gcc does not support in-tree build
          # if we build in-tree with libgcc it will fail with something like: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=32212
          # without libgcc the in-tree build works fine
          preConfigure = ''
            mkdir build
            cd build
          '';

          configureScript = "../configure";

          configureFlags = [
            "--target=funnyarch-none-none"
            "--disable-nls"
            "--disable-multilib"
            "--enable-languages=c,c++"
            "--without-gnu-as"
            "--with-as=${packages.toolchain}/bin/funnyarch-none-none-as"
            "--without-gnu-ld"
            "--with-ld=${packages.toolchain}/bin/funnyarch-none-none-ld"
            "--prefix=/"
            "AR_FOR_TARGET=ar"
            "RANLIB_FOR_TARGET=ranlib"
          ];

          buildPhase = ''
            make -j$NIX_BUILD_CORES all-gcc
            make -j$NIX_BUILD_CORES all-target-libgcc CFLAGS_FOR_TARGET='-fomit-frame-pointer -fno-merge-constants -mno-unaligned-access'
          '';

          installPhase = ''
            mkdir -p "$out"
            DESTDIR="$out" make install-gcc
            DESTDIR="$out" make install-target-libgcc
          '';
        };
      }
    );
}
