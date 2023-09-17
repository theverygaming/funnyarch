memsize:
mov r0, #0x1000 // begin address
mov r4, #0xFFFF // end address
mov r10, #0 // total working memory size in bytes
mov r1, r0 // r1 is current address
.memsize_loop:
ldr r2, r1, #0 // r2 contains data @r1
str r1, r1, #0 // store current address @r1
ldr r3, r1, #0 // r3 contains data @r1
cmp r3, r1
ifeq add r10, #1
stri r1, r2, #1 // restore old data
cmp r1, r4
iflt rjmp .memsize_loop
ret()
