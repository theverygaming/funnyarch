rjmp #0
mov r5, #12
jmp r5
add r1, r0, #5
add r1, r1, r1
add r2, r0, #10
add r3, r1, r2
add r4, r1, r2
add r4, #1
mov r4, r3
mov r3, #5
stri r3, r4, #-1
/*
mov r4, #0x1403
str r10, r4, #1
jmp #0xFFFF
*/
