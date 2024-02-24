//void ia32_gdt_load(gdtr* descriptor, uint16_t codeSegment, uint16_t dataSegment);
.global ia32_gdt_load
ia32_gdt_load:
    pushl %ebp
    movl %esp, %ebp

    // load gdt
    mov 8(%ebp), %eax
    lgdt (%eax)

    // reload CS
    mov 12(%ebp), %eax
    pushl %eax
    pushl $.reload_cs
    retfl

.reload_cs:
    // reload other segments
    mov 16(%ebp), %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    mov %ax, %ss

    mov %ebp, %esp
    popl %ebp
    ret
