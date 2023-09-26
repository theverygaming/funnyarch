.origin 0x0

main:
mov rsp, #0x1000
mov r0, str_hello
rcall(puts)

mov r2, #5
.main_l1:
mov r0, str_hehe
rcall(puts)
sub r2, #1
cmp r2, #0
ifneq rjmp .main_l1
mov r24, #0
str r24, r1, #0
loop:
rjmp loop

#include "macros.asm"

// pointer to string in r0
puts:
.puts_loop:
load_byte_unaligned(r0, r1)
add r0, #1
cmp r1, #0
ifeq rjmp .puts_finish
mov r24, #0
str r24, r1, #0
rjmp .puts_loop
.puts_finish:
ret()

defstr_sm(str_hello, "hello")
defstr_sm(str_hehe, "hehe")
