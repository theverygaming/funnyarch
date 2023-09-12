#!/usr/bin/env bash
set -e

python3 ../assembler/python/assembler.py ../test.asm output.bin

#rm -rf ./obj_dir
verilator --top-module cpu -O3 --trace -cc src/*.v --exe tests/*.cpp # trace
#verilator --top-module cpu -O3 --x-assign fast --x-initial fast --noassert -cc src/*.v --exe tests/*.cpp # no trace
make -j$(nproc) -C obj_dir -f Vcpu.mk Vcpu
echo "running"
./obj_dir/Vcpu
gtkwave waveform.vcd
