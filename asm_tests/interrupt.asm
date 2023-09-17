int_handler:
push(lr)
push(r0)
push(r1)
mov r0, str_gotint
mov r1, #1
rcall(puts)
pop(r1)
pop(r0)
pop(lr)
pop(rf)
pop(rip)

defstr(str_gotint, "hello from interrupt handler!")
