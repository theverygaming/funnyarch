int_handler:
push(lr)
push(r0)
push(r1)
push(r2)
push(r3)
push(r4)
push(r5)
push(r6)
push(r7)
push(r8)
push(r9)
push(rf)

mfsr r2, irip
push(r2)

mfsr r0, pcst
shr r0, r0, #24 // interrupt number in r0

// alignment fault
cmp r0, #254
ifeq mfsr r0, pcst
ifeq xor r0, #0b1 // unset alignment flag
ifeq xor r0, #0b10000 // unset old alignment flag
ifeq mtsr pcst, r0
ifeq rjmp .int_handler_p1

// unknown fault
cmp r0, #253
.int_handler_l1:
ifgteq rjmp .int_handler_l1

.int_handler_p1:
ifeq mov r0, str_alignerr
iflt mov r0, str_gotint
mov r1, #1
rcall(puts)

pop(r2)
mtsr irip, r2

pop(rf)
pop(r9)
pop(r8)
pop(r7)
pop(r6)
pop(r5)
pop(r4)
pop(r3)
pop(r2)
pop(r1)
pop(r0)
pop(lr)
iret

defstr(str_gotint, "hello from interrupt handler!")
defstr(str_alignerr, "alignment error")
