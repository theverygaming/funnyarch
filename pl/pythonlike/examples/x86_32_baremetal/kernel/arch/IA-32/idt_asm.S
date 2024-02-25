//void ia32_idt_load(idtr* descriptor);
.global ia32_idt_load
ia32_idt_load:
    pushl %ebp
    movl %esp, %ebp

    // load idt
    mov 8(%ebp), %eax
    lidt (%eax)

    mov %ebp, %esp
    popl %ebp
    ret

.global ia32_enable_interrupts
ia32_enable_interrupts:
    sti
    ret
