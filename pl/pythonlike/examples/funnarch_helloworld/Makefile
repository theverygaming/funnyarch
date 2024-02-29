ASM = python3 ../../../../assembler/python/assembler.py
COMP = python3 ../../compiler.py --target funnyarch

.PHONY: all
all: demo


demo: demo.bin


.PRECIOUS: demo.asm # for debugging


%.asm: %.py
	@$(COMP) -o $@ $^


%.bin: %.asm
	@$(ASM) $^ output.bin


clean:
	@rm -f demo.bin
