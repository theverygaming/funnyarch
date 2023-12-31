// tmpreg should not have the same register number as regnum
#define sysregtest_test_system_register(regnum, tmpreg) mov tmpreg, #64535 \
                                                        mov regnum, #1 \
                                                        mtsr regnum, tmpreg \
                                                        cmp regnum, #1 \
                                                        ifneq rjmp .regtest_failed \
                                                        mov tmpreg, #5 \
                                                        mfsr tmpreg, regnum \
                                                        cmp tmpreg, #64535 \
                                                        ifneq rjmp .regtest_failed \
                                                        mov tmpreg, #0 \
                                                        movh tmpreg, #64535 \
                                                        mov regnum, #1 \
                                                        mtsr regnum, tmpreg \
                                                        cmp regnum, #1 \
                                                        ifneq rjmp .regtest_failed \
                                                        mov tmpreg, #5 \
                                                        mfsr tmpreg, regnum \
                                                        shr tmpreg, tmpreg, #16 \
                                                        cmp tmpreg, #64535 \
                                                        ifneq rjmp .regtest_failed

sysregtest:
push(lr)
push(r20)
push(r21)

sysregtest_test_system_register(scr0, r1)
sysregtest_test_system_register(scr1, r0)
sysregtest_test_system_register(scr2, r0)
sysregtest_test_system_register(scr3, r0)
sysregtest_test_system_register(irip, r0)
sysregtest_test_system_register(ibptr, r0)
sysregtest_test_system_register(pcst, r0)

mov r1, #0
rjmp .sysregtest_finish

.sysregtest_failed:
mov r1, #1
.sysregtest_finish:
pop(r21)
pop(r20)
mov r0, sysregtest_str
rcall(testresult)
pop(lr)
ret

defstr(sysregtest_str, "system registers")
