cmptest:
push(lr)
mov r1, #0

mov r2, #0
mov r3, #0
cmp r2, r3
ifneq rjmp .cmptest_failed
iflt rjmp .cmptest_failed
ifgt rjmp .cmptest_failed
cmp r2, #0
ifneq rjmp .cmptest_failed
iflt rjmp .cmptest_failed
ifgt rjmp .cmptest_failed

mov r2, #1
mov r3, #50
cmp r2, r3
ifeq rjmp .cmptest_failed
ifgteq rjmp .cmptest_failed
ifgt rjmp .cmptest_failed
cmp r2, #50
ifeq rjmp .cmptest_failed
ifgteq rjmp .cmptest_failed
ifgt rjmp .cmptest_failed

mov r2, #19530
mov r3, #19529
cmp r2, r3
ifeq rjmp .cmptest_failed
iflt rjmp .cmptest_failed
iflteq rjmp .cmptest_failed
cmp r2, #19529
ifeq rjmp .cmptest_failed
iflt rjmp .cmptest_failed
iflteq rjmp .cmptest_failed

mov r2, #63627
mov r3, #63627
cmp r2, r3
ifneq rjmp .cmptest_failed
iflt rjmp .cmptest_failed
ifgt rjmp .cmptest_failed
cmp r2, #63627
ifneq rjmp .cmptest_failed
iflt rjmp .cmptest_failed
ifgt rjmp .cmptest_failed

ifeq rjmp .cmptest_finish

.cmptest_failed:
mov r1, #1
.cmptest_finish:
mov r0, cmptest_str
rcall(testresult)
pop(lr)
ret()

defstr(cmptest_str, "compare")
