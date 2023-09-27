// r0 points to test name string - if r1 is nonzero test failed
testresult:
push(lr)
push(r0)
push(r1)
push(r2)
mov r2, r1
mov r1, #0
push(r0)
mov r0, teststr
rcall(puts)
pop(r0)
rcall(puts)
mov r1, #1
cmp r2, #0
ifeq mov r0, teststr_ok
ifneq mov r0, teststr_fail
rcall(puts)
pop(r2)
pop(r1)
pop(r0)
pop(lr)
ret

defstr(teststr, "TEST '")
defstr(teststr_ok, "' [OK]")
defstr(teststr_fail, "' [FAILED]")
