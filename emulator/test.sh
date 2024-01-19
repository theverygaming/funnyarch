#!/usr/bin/env bash
set -e -o pipefail

#python3 ../assembler/python/assembler.py ../asm/testsuite/main.asm output.bin | tee output.txt
#python3 ../assembler/python/assembler.py ../asm/monitor/main.asm output.bin | tee output.txt
#python3 ../assembler/python/assembler.py ../asm/mandelbrot/main.asm output.bin | tee output.txt
python3 ../assembler/python/assembler.py ../asm/rom/main.asm output.bin | tee output.txt

#python3 ../assembler/python/assembler.py ../asm/videoplayer/main.asm output.bin | tee output.txt
#python3 ../asm/videoplayer/gen.py ../asm/videoplayer/source.mp4 hd.bin

#make clean
#make -j$(nproc) TARGET=linux-gcov
#./emu
#gcov --all-blocks src/cpu.cpp

make -j$(nproc)
./emu
