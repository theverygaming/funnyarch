shifttest:
push(lr)
mov r1, #0

mov r2, #255
mov r3, #5
shl r4, r2, r3
cmp r4, #8160
ifneq rjmp .shifttest_failed
shl r4, r2, #4
cmp r4, #4080
ifneq rjmp .shifttest_failed
mov r3, #32
shl r4, r2, r3
cmp r4, #255
ifneq rjmp .shifttest_failed

mov r2, #255
mov r3, #5
shr r4, r2, r3
cmp r4, #7
ifneq rjmp .shifttest_failed
shr r4, r2, #4
cmp r4, #15
ifneq rjmp .shifttest_failed
mov r3, #31
shr r4, r2, r3
cmp r4, #0
ifneq rjmp .shifttest_failed
mov r2, #0
sub r2, #1
mov r3, #31
shr r4, r2, r3
cmp r4, #1
ifneq rjmp .shifttest_failed

mov r2, #255
mov r3, #5
sar r4, r2, r3
cmp r4, #7
ifneq rjmp .shifttest_failed
sar r4, r2, #4
cmp r4, #15
ifneq rjmp .shifttest_failed
mov r3, #31
sar r4, r2, r3
cmp r4, #0
ifneq rjmp .shifttest_failed
mov r2, #0
sub r2, #1
sar r4, r2, #25
cmp r4, r2
ifneq rjmp .shifttest_failed

rjmp .shifttest_finish

.shifttest_failed:
mov r1, #1
.shifttest_finish:
mov r0, shifttest_str
rcall(testresult)
pop(lr)
ret

defstr(shifttest_str, "shift")
