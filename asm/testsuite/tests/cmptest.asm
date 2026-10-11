#define cmptest_t(cond) cond add rip, rip, #4 \
                        rjmp .cmptest_failed
#define cmptest_f(cond) cond rjmp .cmptest_failed
cmptest:
push(lr)
mov r1, #0

mov r2, #0
mov r3, #0
cmp r2, r3
cmptest_t(ifeq)
cmptest_f(ifneq)
cmptest_f(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_t(ifgteq)
cmp r2, #0
cmptest_t(ifeq)
cmptest_f(ifneq)
cmptest_f(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_t(ifgteq)

mov r2, #1
mov r3, #50
cmp r2, r3
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_t(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_f(ifgteq)
cmp r2, #50
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_t(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_f(ifgteq)

mov r2, #19530
mov r3, #19529
cmp r2, r3
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)
cmp r2, #19529
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)

mov r2, #63627
mov r3, #63627
cmp r2, r3
cmptest_t(ifeq)
cmptest_f(ifneq)
cmptest_f(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_t(ifgteq)
cmp r2, #63627
cmptest_t(ifeq)
cmptest_f(ifneq)
cmptest_f(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_t(ifgteq)

mov r2, #0xF000
movh r2, #0xFFFF
mov r3, #19529
cmp r2, r3
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)
cmp r2, #19529
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_f(iflt)
cmptest_f(iflteq)
cmptest_t(ifgt)
cmptest_t(ifgteq)

mov r2, #0xF000
movh r2, #0xFFFF
mov r3, #0xC000
movh r3, #0xFFFF
cmp r2, r3
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
cmp r2, r3
cmptest_f(ifeq)
cmptest_t(ifneq)
cmptest_t(iflt)
cmptest_t(iflteq)
cmptest_f(ifgt)
cmptest_f(ifgteq)

rjmp .cmptest_finish

.cmptest_failed:
mov r1, #1
.cmptest_finish:
mov r0, cmptest_str
rcall(testresult)
pop(lr)
ret

defstr(cmptest_str, "CMP")
