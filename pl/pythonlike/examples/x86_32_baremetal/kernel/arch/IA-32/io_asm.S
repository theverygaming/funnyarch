.macro outf instr, reg
// ia32_\instr(port, data)
.global ia32_\instr
ia32_\instr:
    mov 4(%esp), %edx
    mov 8(%esp), %eax
    \instr \reg, %dx
    ret
.endm

.macro inf instr, reg
// ia32_\instr(port)
.global ia32_\instr
ia32_\instr:
.if \reg != %eax
    xor %eax, %eax
.endif
    mov 4(%esp), %edx
    \instr %dx, \reg
    ret
.endm


outf outb %al
outf outw %ax
outf outl %eax

inf inb %al
inf inw %ax
inf inl %eax
