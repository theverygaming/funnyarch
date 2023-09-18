addtest:
push(lr)
mov r1, #0

mov r2, #7539
mov r3, #8673
mov r4, #2
add r2, r3, r2
cmp r2, #16212
ifneq rjmp .addtest_failed
add r2, r2, r2
cmp r2, #32424
ifneq rjmp .addtest_failed
add r2, r3, r4
cmp r2, #8675
ifneq rjmp .addtest_failed

mov r2, #255
add r3, r2, #5
cmp r3, #260
ifneq rjmp .addtest_failed
mov r2, #0
add r3, r2, #5
cmp r3, #5
ifneq rjmp .addtest_failed
mov r3, #1678
add r2, r3, #0
cmp r2, #1678
ifneq rjmp .addtest_failed

mov r2, #7839
add r2, #1
cmp r2, #7840
ifneq rjmp .addtest_failed
// TODO: high 16 bits

mov r2, #0
add r2, #0
cmp r2, #0
ifneq rjmp .addtest_failed
ifeq rjmp .addtest_finish

.addtest_failed:
mov r1, #1
.addtest_finish:
mov r0, addtest_str
rcall(testresult)
pop(lr)
ret()

defstr(addtest_str, "ADD")
