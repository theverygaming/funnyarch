.origin 0x0
rjmp main

#include "macros.asm"
#include "io.asm"
#include "tests.asm"
#include "tests/all.asm"

main:
mov rsp, #0x2708
push(lr)
mov r0, str_mainruns
mov r1, #0
rcall(testresult)
rcall(alltests)
//rcall(drawchar)
pop(lr)
jmp #0xFFFF

defstr(str_mainruns, "main runs")

#include "font8x8.asm"

drawchar:
mov r10, #0
mov r4, code_end
mov r1, r4
mov r2, font8x8
.drawchar_p1:
ldr r3, r2, #0
ldr r5, r1, #0
str r1, r3, #0
add r1, #80
add r2, #1
mov r3, font8x8_end
cmp r2, r3
ifgteq add r4, #1
ifgteq mov r1, r4
ifgteq mov r2, font8x8
ifgteq add r10, #1
/*cmp r4, #0x3c4c
ifgteq mov r4, code_end
ifgteq mov r1, r4
ifgteq mov r2, font8x8*/
rjmp .drawchar_p1

ret()

code_end:
