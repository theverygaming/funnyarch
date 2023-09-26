.origin 0x0
rjmp main

#include "macros.asm"
#include "io.asm"
#include "tests.asm"
#include "tests/all.asm"
#include "memsize.asm"
#include "interrupt.asm"

main:
or rf, #0b100 // set alignment flag
mov rsp, #0x23E0
mov iptr, int_handler
int #0 // FIXME: we need a proper test for interrupts (and exceptions)
push(lr)
mov r0, str_mainruns
mov r1, #0
rcall(testresult)
rcall(alltests)
pop(lr)
rcall(memsize)
loop:
rjmp loop
jmp #0xFFFF

defstr(str_mainruns, "main runs")


// multiplies r0 by r1 and returns in r0
mult: // stupid multiply function
push(r1)
push(r2)
mov r2, #0
cmp r1, #0
ifeq rjmp .mult_exit
.mult_l1:
add r2, r2, r0
sub r1, #1
cmp r1, #0
ifneq rjmp .mult_l1
.mult_exit:
mov r0, r2
pop(r2)
pop(r1)
ret()


#include "font8x8.asm"

// character in r0
// r20: x
// r21: y
// r22: width
drawchar:
mov r22, #80 // 640 / 8
push(lr)
push(r0)
push(r1)
push(r2)
push(r3)
push(r4)
push(r5)
push(r6)
push(r7)

// if newline
cmp r0, #0x0A
ifeq mov r20, #0
ifeq add r21, #1
ifeq rjmp .drawchar_cleanup

// map character to font index
// if character is between 'a'(0x61) and 'z'(0x7a)
cmp r0, #0x61
iflt rjmp .drawchar_caps
cmp r0, #0x7a
ifgt rjmp .drawchar_caps
sub r0, r0, #0x20 // convert to uppercase
// if character is between 'A'(0x41) and 'Z'(0x5a)
.drawchar_caps:
cmp r0, #0x41
iflt rjmp .drawchar_finish
cmp r0, #0x5a
ifgt rjmp .drawchar_finish
sub r0, r0, #0x41

shl r0, r0, #3 // multiply character index by 8 since font is 8x8

mov r3, #0xFF // mask in r3
not r4, r3 // inverted mask in r4

mov r1, font8x8 // font pointer
add r1, r1, r0 // add offset to font pointer
mov r2, #0x3000 // framebuffer pointer
// add x and y to framebuffer pointer
push(r20)
push(r1)
push(r0)
// multiplies r0 by r1 and returns in r0
mov r0, r22 // width in r0
mov r1, r21 // y in r1
shl r1, r1, #3 // multiply y by 8
rcall(mult)
add r2, r2, r0

shr r20, r20, #3 // divide x by 8
add r2, r2, r20

pop(r0)
pop(r1)
pop(r20)

mov r7, #8 // loop len

.drawchar_l1:
ldr r5, r2, #0 // current contents of FB word in r5
and r5, r5, r4 // use reverse mask on old FB contents
ldr r6, r1, #0 // get font word in r6
and r6, r6, r3 // use mask on font word
or r5, r5, r6 // or the two together
str r2, r5, #0 // store it in FB

add r2, r2, r22 // add width to FB pointer
add r1, r1, #1 // add 1 to font pointer
sub r7, r7, #1 // loop n
cmp r7, #0
ifneq rjmp .drawchar_l1

.drawchar_finish:
// move pointer further
add r20, #8
push(r22)
shl r22, r22, #3 // r22 * 8
cmp r20, r22 // if x >= width
pop(r22)
ifgteq mov r20, #0
ifgteq add r21, #1
cmp r21, #480
ifgteq mov r21, #0
ifgteq mov r20, #0

.drawchar_cleanup:
pop(r7)
pop(r6)
pop(r5)
pop(r4)
pop(r3)
pop(r2)
pop(r1)
pop(r0)
pop(lr)
ret()
