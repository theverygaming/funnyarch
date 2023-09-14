subtest:
push(lr)
mov r1, #0

mov r2, #7539
mov r3, #8673
mov r4, #2
sub r2, r3, r2
cmp r2, #1134
ifneq rjmp .subtest_failed
sub r2, r2, r2
cmp r2, #0
ifneq rjmp .subtest_failed
sub r2, r3, r4
cmp r2, #8671
ifneq rjmp .subtest_failed

mov r2, #255
sub r3, r2, #5
cmp r3, #250
ifneq rjmp .subtest_failed
mov r2, #5
sub r3, r2, #0
cmp r3, #5
ifneq rjmp .subtest_failed
mov r3, #1678
sub r2, r3, #0
cmp r2, #1678
ifneq rjmp .subtest_failed

mov r2, #7839
sub r2, #1
cmp r2, #7838
ifneq rjmp .subtest_failed

mov r2, #0
sub r2, #0
cmp r2, #0
ifneq rjmp .subtest_failed
ifeq rjmp .subtest_finish

.subtest_failed:
mov r1, #1
.subtest_finish:
mov r0, subtest_str
rcall(testresult)
pop(lr)
ret()

defstr(subtest_str, "subtraction")
