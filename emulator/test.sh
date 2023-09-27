#!/usr/bin/env bash
set -e -o pipefail

python3 ../assembler/python/assembler.py ../asm/testsuite/main.asm output.bin | tee output.txt


make -j12 
./emu
