#define regtest_test_register(regnum) mov regnum, #0 \
                              cmp regnum, #0 \
                              ifneq rjmp .regtest_failed \
                              movh regnum, #1 \
                              shr regnum, regnum, #16 \
                              cmp regnum, #1 \
                              ifneq rjmp .regtest_failed \
                              mov regnum, #65535 \
                              sub regnum, #1 \
                              cmp regnum, #65534 \
                              ifneq rjmp .regtest_failed \
                              sub regnum, #65534 \
                              movh regnum, #65334 \
                              shr regnum, regnum, #16 \
                              cmp regnum, #65334 \
                              ifneq rjmp .regtest_failed

regtest:
push(lr)
push(r20)
push(r21)

regtest_test_register(r0)
regtest_test_register(r1)
regtest_test_register(r2)
regtest_test_register(r3)
regtest_test_register(r4)
regtest_test_register(r5)
regtest_test_register(r6)
regtest_test_register(r7)
regtest_test_register(r8)
regtest_test_register(r9)
regtest_test_register(r10)
regtest_test_register(r11)
regtest_test_register(r12)
regtest_test_register(r13)
regtest_test_register(r14)
regtest_test_register(r15)
regtest_test_register(r16)
regtest_test_register(r17)
regtest_test_register(r18)
regtest_test_register(r19)
regtest_test_register(r20)
regtest_test_register(r21)
regtest_test_register(r22)
regtest_test_register(r23)
regtest_test_register(r24)
regtest_test_register(r25)
regtest_test_register(r26)
regtest_test_register(rfp)
regtest_test_register(lr)

mov r1, #0
rjmp .regtest_finish

.regtest_failed:
mov r1, #1
.regtest_finish:
pop(r21)
pop(r20)
mov r0, regtest_str
rcall(testresult)
pop(lr)
ret

defstr(regtest_str, "registers")
