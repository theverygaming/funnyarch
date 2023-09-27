.NOTPARALLEL:

.PHONY: all
all: test emulator emulator_fpga

.PHONY: clean
clean:
	rm -rf out/
	rm -rf obj_dir/
	rm -f emulator emulator_fpga output.bin output.txt
	rm -f icebreaker.asc icebreaker.bin icebreaker.json icebreaker.log
	rm -f hex_memory_file.mem src/hex_memory_file.mem

.PHONY: test
test: out/testbench_alu out/testbench_cpu
	@for f in $^; do echo "-- running testbench $$f --"; ./$$f; done
	@for f in $^; do echo "-- generating coverage report for $$f --"; mkdir -p out/coverage/$$f; verilator_coverage $${f}_coverage.dat --annotate-min 10 --annotate out/coverage/$$f; done
	@echo "-- coverage rank --"
	@verilator_coverage --rank $(addsuffix _coverage.dat,$^)

out/testbench_%: tests/testbench_%.cpp src/%.v
	verilator -Isrc/ --trace --top-module $* -cc $*.v --exe $< --CFLAGS "-DCOVERAGE" --coverage
	make -C obj_dir -f V$*.mk
	mkdir -p out
	cp obj_dir/V$* out/testbench_$*

output.bin: ../asm/testsuite/**
	python3 ../assembler/python/assembler.py ../asm/testsuite/main.asm output.bin

emulator: src/* emu/* output.bin
	verilator --top-module cpu -O3 --x-assign fast --x-initial fast --noassert -cc src/*.v --exe emu/*.cpp --CFLAGS "`sdl2-config --cflags`" --LDFLAGS "`sdl2-config --libs`"
	make -C obj_dir -f Vcpu.mk OPT_FAST="-O3 -march=native"
	cp obj_dir/Vcpu emulator

emulator_fpga: src/* emu_fpga/* output.bin
	python3 bin2h.py > hex_memory_file.mem
	verilator -Isrc/ --top-module fpga_cpu_top -O3 --x-assign fast --x-initial fast --noassert -cc src/*.v --exe emu_fpga/*.cpp --CFLAGS "`sdl2-config --cflags`" --LDFLAGS "`sdl2-config --libs`"
	make -C obj_dir -f Vfpga_cpu_top.mk OPT_FAST="-O3 -march=native"
	cp obj_dir/Vfpga_cpu_top emulator_fpga

.PHONY: synth-icebreaker
synth-icebreaker: icebreaker.bin

icebreaker.bin: src/* output.bin
	python3 bin2h.py > hex_memory_file.mem
	yosys -ql icebreaker.log -p "synth_ice40 -top top -json icebreaker.json" fpga/icebreaker/icebreaker.v src/alu.v src/control.v src/cpu.v src/fpga_cpu_top.v
	nextpnr-ice40 --up5k --package sg48 --json icebreaker.json --pcf fpga/icebreaker/icebreaker.pcf --asc icebreaker.asc
	icepack icebreaker.asc icebreaker.bin
