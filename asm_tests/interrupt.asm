int_handler:
push(lr)
push(r0)
push(r1)

shr r0, rf, #24 // interrupt number in r0
cmp r0, #254
ifeq ldr r0, rsp, #12
ifeq xor r0, #0b100 // unset alignment flag on stack
ifeq str rsp, r0, #12
ifeq xor rf, #0b100 // unset alignment flag
ifeq rjmp .int_handler_p1
.int_handler_l1:
ifgteq rjmp .int_handler_l1

.int_handler_p1:
ifeq mov r0, str_alignerr
iflt mov r0, str_gotint
mov r1, #1
rcall(puts)

pop(r1)
pop(r0)
pop(lr)
pop(rf)
pop(rip)

defstr(str_gotint, "hello from interrupt handler!")
defstr(str_alignerr, "alignment error")
