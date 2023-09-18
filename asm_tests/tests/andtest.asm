andtest:
push(lr)
mov r1, #1
mov r2, #0

// TODO: other encodings

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
