CC = gcc
CFLAGS = -ffreestanding -nostdlib

COMP = python3 ../../compiler.py

.PHONY: all
all: demo


demo: demo.o syscall.o
	@$(CC) $(CFLAGS) -o $@ $^


%.c: %.py
	@$(COMP) -o $@ $^

%.o: %.c
	@$(CC) $(CFLAGS) -o $@ -c $^


%.o: %.S
	@$(CC) $(CFLAGS) -o $@ -c $^

clean:
	@rm -f demo.o syscall.o
	@rm -f demo
