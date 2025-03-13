#!/usr/bin/env bash
set -e -o pipefail

nix-shell --pure shell_windows.nix --run "./build_windows_inshell.sh"
