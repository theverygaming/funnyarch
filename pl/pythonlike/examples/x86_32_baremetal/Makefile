CC = i686-elf-gcc
LD = i686-elf-ld
CFLAGS = -O3 -ffreestanding -nostdlib

COMP = python3 ../../compiler.py

.PHONY: all
all: boot.iso

OBJS = obj/kernel/kmain.o \
	   obj/kernel/arch/IA-32/init.o \
	   obj/kernel/arch/IA-32/mem.o \
	   obj/kernel/arch/IA-32/gdt.o \
	   obj/kernel/arch/IA-32/gdt_asm.o \
	   obj/kernel/arch/IA-32/idt.o \
	   obj/kernel/arch/IA-32/idt_asm.o \
	   obj/kernel/arch/IA-32/printk.o

obj/kernel.o: obj/kernel/arch/IA-32/boot.o $(OBJS)
	@$(LD) -T kernel/linker.ld -nostdlib $(filter %.o,$^) -o $@

boot.iso: obj/kernel.o 
	@./boot/createimg.sh

.PRECIOUS: obj/%.c
obj/%.c: %.py
	@mkdir -p $(dir $@)
	@$(COMP) -o $@ $<

obj/%.o: %.c
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -o $@ -c $<

obj/%.o: %.S
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -o $@ -c $<

clean:
	@rm -rf obj/
	@rm -f boot.iso
