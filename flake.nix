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
            cp -r objcopy.py "$out/bin/funnyarch-none-none-objcopy"
            cp -r nm.py "$out/bin/funnyarch-none-none-nm"

            # standard system ar & ranlib work just fine!
            ln -s "${pkgs.binutils}/bin/ar" "$out/bin/funnyarch-none-none-ar"
            ln -s "${pkgs.binutils}/bin/ranlib" "$out/bin/funnyarch-none-none-ranlib"
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
            funnyarch-none-none-ld --origin 0 -o rom_linked.o rom.o
            funnyarch-none-none-objcopy -O binary rom_linked.o rom.bin
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
        packages.emulator-nographics = packages.emulator.overrideAttrs (
          finalAttrs: previousAttrs: {
            env.NIX_CFLAGS_COMPILE = "-D NO_GRAPHICS";
            installPhase = ''
              mkdir -p "$out/bin"
              cp emu "$out/bin"/funnyarch-emulator-nographics
            '';
          }
        );
        packages.gcc = pkgs.stdenv.mkDerivation rec {
          name = "gcc-funnyarch-none-none";

          src = pkgs.fetchurl {
            url = "https://ftp.fu-berlin.de/unix/languages/gcc/releases/gcc-16.2.0/gcc-16.2.0.tar.xz";
            sha256 = "sha256-5nOOKVl/czJwcxqpBgDzf/3ARQed/CfsfoGSzIEIXD4=";
          };

          patches = [
            # fetchpatch somehow breaks the patch so??? we just use fetchurl fuck it
            (pkgs.fetchurl {
              name = "funnyarch.patch";
              url = "https://github.com/theverygaming/gcc/compare/1b961bf9d7e76de9a36f93d8749dbe7fae302246...4f5bebe181fdd0414e395902c30954b3f2622081.patch";
              sha256 = "sha256-qwfsd7LY+eB84k7+rrla8CIZuSTyIqUy5EW14rzNOpM=";
            })
          ];

          # somehow breaks our config.sub modifications???
          updateAutotoolsGnuConfigScriptsPhase = "true";

          nativeBuildInputs = [
            pkgs.gmp
            pkgs.mpfr
            pkgs.libmpc
            pkgs.flex
            pkgs.bison
            pkgs.gnat16
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
            "--enable-languages=c,c++,ada"
            "--without-gnu-as"
            "--with-as=${packages.toolchain}/bin/funnyarch-none-none-as"
            "--without-gnu-ld"
            "--with-ld=${packages.toolchain}/bin/funnyarch-none-none-ld"
            "--prefix=/"
            "AR_FOR_TARGET=${pkgs.stdenv.cc.bintools}/bin/ar"
            "RANLIB_FOR_TARGET=${pkgs.stdenv.cc.bintools}/bin/ranlib"
          ];

          buildPhase = ''
            make -j$NIX_BUILD_CORES all-gcc
            make -j$NIX_BUILD_CORES all-target-libgcc CFLAGS_FOR_TARGET='-fomit-frame-pointer -fno-merge-constants -mno-unaligned-access -fpic -mpic-data-is-text-relative'
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
