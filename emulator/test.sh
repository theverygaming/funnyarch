#!/usr/bin/env bash
set -e -o pipefail

python3 ../assembler/python/assembler.py ../asm/testsuite/main.asm output.bin | tee output.txt
#python3 ../assembler/python/assembler.py ../asm/monitor/main.asm output.bin | tee output.txt

make -j12
./emu
