addtest:
push(lr)
mov r1, #0
// FIXME
.addtest_failed:
add r1, #1
.addtest_finish:
mov r0, addtest_str
rcall(testresult)
pop(lr)
ret()

defstr(addtest_str, "addition")
