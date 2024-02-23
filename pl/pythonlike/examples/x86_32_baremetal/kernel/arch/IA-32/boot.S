.section .entry

    // multiboot header alignment
    .align 8
multiboot_header:
    .long 0xe85250d6 // magic number
    .long 0 // architecture -> 0 = 32-bit protected mode i386
    .long multiboot_header_end - multiboot_header
    // checksum
    .long -(0xe85250d6 + 0 + (multiboot_header_end - multiboot_header))
    // end tag
    .short 0
    .short 0
    .long 8
multiboot_header_end:

.section .text

#define STACK_SIZE 4096

.global _start
_start:
    // stack
    movl $(stack + STACK_SIZE), %esp

    // reset eflags
    pushl $0
    popf

    // mb2 info stuct
    pushl %ebx
    // magic value
    pushl %eax
    call ia32_init

hlt:
    jmp hlt

.comm stack, STACK_SIZE, 4
