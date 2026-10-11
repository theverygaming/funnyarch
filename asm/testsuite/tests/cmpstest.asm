#define cmpstest_t(cond) cond add rip, rip, #4 \
                        rjmp .cmpstest_failed
#define cmpstest_f(cond) cond rjmp .cmpstest_failed
cmpstest:
push(lr)
mov r1, #0

mov r2, #0
mov r3, #0
cmps r2, r3
cmpstest_t(ifeq)
cmpstest_f(ifneq)
cmpstest_f(iflt)
cmpstest_t(iflteq)
cmpstest_f(ifgt)
cmpstest_t(ifgteq)
cmps r2, #0
cmpstest_t(ifeq)
cmpstest_f(ifneq)
cmpstest_f(iflt)
cmpstest_t(iflteq)
cmpstest_f(ifgt)
cmpstest_t(ifgteq)

mov r2, #1
mov r3, #50
cmps r2, r3
cmpstest_f(ifeq)
cmpstest_t(ifneq)
cmpstest_t(iflt)
cmpstest_t(iflteq)
cmpstest_f(ifgt)
cmpstest_f(ifgteq)
cmps r2, #50
cmpstest_f(ifeq)
cmpstest_t(ifneq)
cmpstest_t(iflt)
cmpstest_t(iflteq)
cmpstest_f(ifgt)
cmpstest_f(ifgteq)

mov r2, #19530
mov r3, #19529
cmps r2, r3
cmpstest_f(ifeq)
cmpstest_t(ifneq)
cmpstest_f(iflt)
cmpstest_f(iflteq)
cmpstest_t(ifgt)
cmpstest_t(ifgteq)
cmps r2, #19529
cmpstest_f(ifeq)
cmpstest_t(ifneq)
cmpstest_f(iflt)
cmpstest_f(iflteq)
cmpstest_t(ifgt)
cmpstest_t(ifgteq)

mov r2, #63627
mov r3, #63627
cmps r2, r3
cmpstest_t(ifeq)
cmpstest_f(ifneq)
cmpstest_f(iflt)
cmpstest_t(iflteq)
cmpstest_f(ifgt)
cmpstest_t(ifgteq)
cmps r2, #63627 // this will turn into a *negative* number (in contrast to the result above) so the result after this is completely different
cmpstest_f(ifeq)
cmpstest_t(ifneq)
cmpstest_f(iflt)
cmpstest_f(iflteq)
cmpstest_t(ifgt)
cmpstest_t(ifgteq)

mov r2, #0xF000
movh r2, #0xFFFF
mov r3, #19529
cmps r2, r3
cmpstest_f(ifeq)
cmpstest_t(ifneq)
cmpstest_t(iflt)
cmpstest_t(iflteq)
cmpstest_f(ifgt)
cmpstest_f(ifgteq)
cmps r2, #19529
cmpstest_f(ifeq)
cmpstest_t(ifneq)
cmpstest_t(iflt)
cmpstest_t(iflteq)
cmpstest_f(ifgt)
cmpstest_f(ifgteq)

mov r2, #0xF000
movh r2, #0xFFFF
mov r3, #0xC000
movh r3, #0xFFFF
cmps r2, r3
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)
cmps r2, #-16384
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)

mov r2, #0xC000
movh r2, #0x7FFF
mov r3, #0xC000
movh r3, #0xFFFF
cmps r2, r3
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)
cmps r2, #-16384
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)

mov r2, #0xC79E
movh r2, #0xFFFF
mov r3, r2
cmps r2, r3
cmptest_t(ifeq)
cmptest_f(ifneq)
cmptest_f(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_t(ifgteq)
cmps r2, #-14434
cmptest_t(ifeq)
cmptest_f(ifneq)
cmptest_f(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_t(ifgteq)

rjmp .cmpstest_finish

.cmpstest_failed:
mov r1, #1
.cmpstest_finish:
mov r0, cmpstest_str
rcall(testresult)
pop(lr)
ret

defstr(cmpstest_str, "CMPS")
