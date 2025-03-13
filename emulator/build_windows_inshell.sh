#!/usr/bin/env bash
set -e -o pipefail

make -j$(nproc) TARGET=windows

cp $SDL2_DLL .


wine ./emu.exe
