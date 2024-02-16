AS = python3 ../assembler/python/assembler.py

.PHONY: all
all: kernel.bin


rom.bin:
	$(AS) ../asm/rom/main.asm $@ > output_rom.log
	cat output_rom.log

ASMFILES_BOOTLOADER = $(shell find ./bootloader -name '*.asm')
bootloader.bin: $(ASMFILES_BOOTLOADER)
	$(AS) bootloader/main.asm $@ > output_bootloader.log
	cat output_bootloader.log

ASMFILES_KERNEL = $(shell find ./kernel -name '*.asm')
kernel.bin: $(ASMFILES_KERNEL)
	$(AS) kernel/main.asm $@ > output_kernel.log
	cat output_kernel.log

genfs: genfs.cpp
	g++ -o $@ $^

ls: ls.cpp drv.h
	g++ -o $@ ls.cpp

run: rom.bin bootloader.bin
	cp rom.bin output.bin
	cp bootloader.bin hd.bin
	ls -lah hd.bin
	../emulator/emu

clean:
	rm -f kernel.bin rom.bin
	rm -f hd.bin output.bin
	rm -f output_rom.log output_kernel.log output_bootloader.log
