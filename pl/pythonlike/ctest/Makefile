CC = gcc
CFLAGS = -ffreestanding -nostdlib

.PHONY: all
all: test


test: test.o syscall.o
	@$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	@$(CC) $(CFLAGS) -o $@ -c $^

%.o: %.S
	@$(CC) $(CFLAGS) -o $@ -c $^
