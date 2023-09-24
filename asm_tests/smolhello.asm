.origin 0x0

main:
mov r0, str_hello
rcall(puts)

mov r1, #5
.main_l1:
mov r0, str_hehe
rcall(puts)
sub r1, #1
cmp r1, #0
ifneq rjmp .main_l1
loop:
rjmp loop

#include "macros.asm"

// pointer to string in r0
puts:
.puts_loop:
ldri r1, r0, #1
and r1, #0xFF
cmp r1, #0
ifeq rjmp .puts_finish
mov r24, r1
rjmp .puts_loop
.puts_finish:
ret()

defstr_sm(str_hello, "hello")
defstr_sm(str_hehe, "hehe")
