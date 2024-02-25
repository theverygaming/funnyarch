ia32_isr_common:
    call ia32_handle_int
    add $8, %esp // pop error code & interrupt number
    iretl

.macro isr n, err=0
ia32_isr_stub_\n:
.if \err == 0
    pushl $0 // dummy error code
.endif
    pushl $\n
    jmp ia32_isr_common
.endm

isr 0    // division error
isr 1    // debug
isr 2    // NMI
isr 3    // breakpoint
isr 4    // overflow
isr 5    // bound range exceeded
isr 6    // invalid opcode
isr 7    // device not available
isr 8  0 // double fault
isr 9    // Coprocessor segment overrun (doesn't exist anymore)
isr 10 0 // invalid TSS
isr 11 0 // segment not present
isr 12 0 // Stack segment fault
isr 13 0 // GP fault
isr 14 0 // Page fault
isr 15   // reserved
isr 16   // x87 FP exception
isr 17 0 // alignment check
isr 18   // machine check
isr 19   // SIMD FP exception
isr 20   // Virtualization exception
isr 21 0 // control protection exception
isr 22   // reserved
isr 23   // reserved
isr 24   // reserved
isr 25   // reserved
isr 26   // reserved
isr 27   // reserved
isr 28   // Hypervisor injection exception
isr 29 0 // VMM communication exception
isr 30 0 // Security exception
isr 31   // reserved

.altmacro
.set i,32
.rept 224
    isr %i
    .set i, i+1
.endr
.noaltmacro

.section .data
.global ia32_idt_arr
.align 8
ia32_idt_arr:
.altmacro
.macro idt_arr_ent n
    .long ia32_isr_stub_\n
    .long 0
.endm
.set i,0
.rept 256
    idt_arr_ent %i
    .set i, i+1
.endr
.noaltmacro
