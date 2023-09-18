nottest:
push(lr)
mov r1, #0

mov r2, #0x6968
not r3, r2
and r3, #0xFFFF
cmp r3, #0x9697
ifneq rjmp .nottest_failed

mov r2, #0
not r2, r2
cmp r2, #0xFFFF
ifeq rjmp .nottest_failed
and r2, #0xFFFF
cmp r2, #0xFFFF
ifneq rjmp .nottest_failed

rjmp .nottest_finish

.nottest_failed:
mov r1, #1
.nottest_finish:
mov r0, nottest_str
rcall(testresult)
pop(lr)
ret()

defstr(nottest_str, "NOT")
