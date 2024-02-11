.section .text
.global do_linux_syscall
do_linux_syscall:
    mov %rdi, %rax
    mov %rsi, %rdi
    mov %rdx, %rsi
    mov %rcx, %rdx
    syscall
    ret

.section .note.GNU-stack,"",@progbits
