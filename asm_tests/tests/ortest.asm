ortest:
push(lr)
mov r1, #0

mov r2, #0x6968
or r3, r2, r2
cmp r3, r2
ifneq rjmp .ortest_failed
mov r2, #0x333A
or r3, r3, r2
cmp r3, #0x7b7a
ifneq rjmp .ortest_failed

mov r2, #0x6568
or r3, r2, #0x49
cmp r3, #0x6569
ifneq rjmp .ortest_failed
mov r2, #0x6568
or r3, r2, #0x9bf
cmp r3, #0x6dff
ifneq rjmp .ortest_failed

mov r2, #0x7866
or r2, #0x656F
cmp r2, #0x7d6f
ifneq rjmp .ortest_failed
// TODO: high 16 bits

rjmp .ortest_finish

.ortest_failed:
mov r1, #1
.ortest_finish:
mov r0, ortest_str
rcall(testresult)
pop(lr)
ret()

defstr(ortest_str, "OR")
