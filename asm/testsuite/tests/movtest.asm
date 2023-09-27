movtest:
push(lr)
mov r1, #0

mov r2, #0
movh r2, #1
shr r2, r2, #16
cmp r2, #1
ifneq rjmp .movtest_failed

mov r2, #1
movh r2, #0
cmp r2, #0
ifeq rjmp .movtest_failed

movh r2, #1
mov r2, #0
cmp r2, #0
ifneq rjmp .movtest_failed

mov r2, #0
movh r2, #1
cmp r2, #0
ifeq rjmp .movtest_failed


rjmp .movtest_finish

.movtest_failed:
mov r1, #1
.movtest_finish:
mov r0, movtest_str
rcall(testresult)
pop(lr)
ret

defstr(movtest_str, "MOV")
