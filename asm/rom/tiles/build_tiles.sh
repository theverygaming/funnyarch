#/usr/bin/env bash
set -e
nix run nixpkgs#imagemagick -- mem.png -threshold 50% -negate MONO:mem.raw
nix run nixpkgs#imagemagick -- nomem.png -threshold 50% -negate MONO:nomem.raw
nix run nixpkgs#imagemagick -- boot.png -threshold 50% -negate MONO:boot.raw
nix run nixpkgs#imagemagick -- nomagic.png -threshold 50% -negate MONO:nomagic.raw
nix run nixpkgs#imagemagick -- w.png -threshold 50% -negate MONO:w.raw
