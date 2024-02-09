// void sched_switch(struct ctx **old, struct ctx *_new);
switch:
push(lr)
push(rfp)
mov rfp, rsp

// save all callee-saved registers
push(r8)
push(r9)
push(r10)
push(r11)
push(r12)
push(r13)
push(r14)
push(r15)
push(r16)
push(r17)
push(r18)
push(r19)
push(r20)
push(r21)
push(r22)
push(r23)
push(r24)
push(r25)
push(r26)

// switch stacks
str r0, rsp, #0
mov rsp, r1

// restore all callee-saved registers
pop(r26)
pop(r25)
pop(r24)
pop(r23)
pop(r22)
pop(r21)
pop(r20)
pop(r19)
pop(r18)
pop(r17)
pop(r16)
pop(r15)
pop(r14)
pop(r13)
pop(r12)
pop(r11)
pop(r10)
pop(r9)
pop(r8)
pop(rfp)
pop(lr)

ret
