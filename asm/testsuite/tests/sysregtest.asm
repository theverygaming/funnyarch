// tmpreg should not have the same register number as regnum
#define sysregtest_test_system_register(regnum, tmpreg, testnumber) mov tmpreg, #testnumber \
                                                        mov regnum, #1 \
                                                        mtsr regnum, tmpreg \
                                                        cmp regnum, #1 \
                                                        ifneq rjmp .sysregtest_failed \
                                                        mov tmpreg, #5 \
                                                        mfsr tmpreg, regnum \
                                                        cmp tmpreg, #testnumber \
                                                        ifneq rjmp .sysregtest_failed \
                                                        mov tmpreg, #0 \
                                                        movh tmpreg, #testnumber \
                                                        mov regnum, #1 \
                                                        mtsr regnum, tmpreg \
                                                        cmp regnum, #1 \
                                                        ifneq rjmp .sysregtest_failed \
                                                        mov tmpreg, #5 \
                                                        mfsr tmpreg, regnum \
                                                        shr tmpreg, tmpreg, #16 \
                                                        cmp tmpreg, #testnumber \
                                                        ifneq rjmp .sysregtest_failed

sysregtest:
push(lr)
push(r20)
push(r21)

sysregtest_test_system_register(scr0, r1, 65237)
sysregtest_test_system_register(scr1, r0, 65237)
sysregtest_test_system_register(scr2, r0, 65237)
sysregtest_test_system_register(scr3, r0, 65237)
sysregtest_test_system_register(irip, r0, 65237)
mfsr r1, ibptr
sysregtest_test_system_register(ibptr, r0, 65237)
mtsr ibptr, r1
sysregtest_test_system_register(pcst, r0, 65233)
sysregtest_test_system_register(tlbirip, r0, 65237)
mfsr r1, tlbiptr
sysregtest_test_system_register(tlbiptr, r0, 65237)
mtsr tlbiptr, r1
sysregtest_test_system_register(tlbflt, r0, 65237)

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
