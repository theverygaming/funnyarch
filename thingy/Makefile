.PHONY: all
all: kernel.bin


ASMFILES_KERNEL = $(shell find ./kernel -name '*.asm')

kernel.bin: $(ASMFILES_KERNEL)
	python3 ../assembler/python/assembler.py kernel/main.asm $@ > output_kernel.log
	cat output_kernel.log


rom.bin:
	python3 ../assembler/python/assembler.py ../asm/rom/main.asm $@ > output_rom.log
	cat output_rom.log

run: rom.bin kernel.bin
	cp rom.bin output.bin
	cp kernel.bin hd.bin
	ls -lah kernel.bin
	../emulator/emu

clean:
	rm -f kernel.bin rom.bin
	rm -f hd.bin output.bin
	rm -f output_rom.log output_kernel.log
