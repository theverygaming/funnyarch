xortest:
push(lr)
mov r1, #1

mov r2, #0x6968
xor r3, r2, r2
cmp r3, #0
ifneq rjmp .xortest_failed
mov r2, #0x333A
xor r3, r3, r2
cmp r3, #0x333A
ifneq rjmp .xortest_failed

mov r2, #0x6568
xor r3, r2, #0x49
cmp r3, #0x6521
ifneq rjmp .xortest_failed
mov r2, #0x6568
xor r3, r2, #0x9bf
cmp r3, #0x6cd7
ifneq rjmp .xortest_failed

mov r2, #0x7866
xor r2, #0x656F
cmp r2, #0x1d09
ifneq rjmp .xortest_failed
// TODO: high 16 bits

xor r1, r1, r1
rjmp .xortest_finish

.xortest_failed:
mov r1, #1
.xortest_finish:
mov r0, xortest_str
rcall(testresult)
pop(lr)
ret()

defstr(xortest_str, "XOR")
