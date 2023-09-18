andtest:
push(lr)
mov r1, #1

mov r2, #0x6968
and r3, r2, r2
cmp r3, r2
ifneq rjmp .andtest_failed
mov r2, #0x333A
and r3, r3, r2
cmp r3, #0x2128
ifneq rjmp .andtest_failed

mov r2, #0x6568
and r3, r2, #0x49
cmp r3, #0x48
ifneq rjmp .andtest_failed
mov r2, #0x6568
and r3, r2, #0x9bf
cmp r3, #0x128
ifneq rjmp .andtest_failed

mov r2, #0x7866
and r2, #0x656F
cmp r2, #0x73
ifeq rjmp .andtest_failed
cmp r2, #0x6066
ifneq rjmp .andtest_failed
// TODO: high 16 bits


mov r2, #0
and r1, r1, r2
rjmp .andtest_finish

.andtest_failed:
mov r1, #1
.andtest_finish:
mov r0, andtest_str
rcall(testresult)
pop(lr)
ret()

defstr(andtest_str, "AND")
