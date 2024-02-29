CC = i686-elf-gcc
LD = i686-elf-ld
CFLAGS = -O3 -nostdlib -fno-pie -mno-red-zone -ffreestanding -fno-exceptions -mno-mmx -mno-sse -mno-sse2 -Wall -Wextra -Wpedantic -Werror -Wno-unused-but-set-variable

COMP = python3 ../../compiler.py --target c

.PHONY: all
all: boot.iso

PYFILES = $(shell find ./kernel -type f -name "*.py")
ASMFILES= $(shell find ./kernel -type f -name "*.S")

OBJS = $(addprefix obj/,$(PYFILES:.py=.o) $(ASMFILES:.S=.o))

obj/kernel.o: $(OBJS)
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

obj/%.o: obj/%.c
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -o $@ -c $<

obj/%.o: %.S
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -o $@ -c $<

clean:
	@rm -rf obj/
	@rm -f boot.iso
