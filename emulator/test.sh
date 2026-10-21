#!/usr/bin/env bash
set -e -o pipefail

#python3 ../assembler/python/assembler.py ../asm/testsuite/main.asm -o output.o
#python3 ../assembler/python/assembler.py ../asm/monitor/main.asm -o output.o
#python3 ../assembler/python/assembler.py ../asm/mandelbrot/main.asm -o output.o
python3 ../assembler/python/assembler.py ../asm/rom/main.asm -o output.o

#python3 ../assembler/python/assembler.py ../asm/videoplayer/main.asm -o output.o
#python3 ../asm/videoplayer/gen.py ../asm/videoplayer/source.mp4 hd.bin

python3 ../assembler/python/linker.py --origin 0 -o output.bin output.o

#make clean
#make -j$(nproc) TARGET=linux-gcov
#./emu
#gcov --all-blocks src/cpu.cpp

make -j$(nproc)
./emu -r output.bin -d hd.bin
