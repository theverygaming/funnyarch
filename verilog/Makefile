.NOTPARALLEL:

.PHONY: all
all: test emulator

.PHONY: clean
clean:
	rm -rf out/
	rm -rf obj_dir/
	rm -f emulator output.bin

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

output.bin: ../asm_tests/**
	python3 ../assembler/python/assembler.py ../asm_tests/main.asm output.bin

emulator: src/* emu/* output.bin
	verilator --top-module cpu -O3 --x-assign fast --x-initial fast --noassert -cc src/*.v --exe emu/*.cpp --CFLAGS "`sdl2-config --cflags`" --LDFLAGS "`sdl2-config --libs`"
	make -C obj_dir -f Vcpu.mk OPT_FAST="-O3 -march=native"
	cp obj_dir/Vcpu emulator
