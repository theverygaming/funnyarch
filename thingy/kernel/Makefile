AS = python3 ../../assembler/python/assembler.py
IDK = python3 ../../pl/idfkanymore_compiler.py
LD = python3 ../../assembler/python/linker.py

.PHONY: all
all: kernel.bin

SOURCES = $(shell find . -name '*.idk' -o -name '*.asm')
OBJS = $(addsuffix .o, $(basename $(SOURCES)))
kernel.bin: $(OBJS)
	$(LD) --origin 8192 -o $@ $^

%.o: %.asm
	$(AS) $^ $@

%.asm: %.idk
	$(IDK) -o $@ --target funnyarch $^

clean:
	rm -f $(OBJS)
