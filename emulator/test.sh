#!/usr/bin/env bash
set -e

python3 ../assembler/python/assembler.py ../asm_tests/main.asm output.bin

python3 ../assembler/python/assembler.py ../asm_tests/main.asm output.bin > output.txt


make -j12 
./emu
