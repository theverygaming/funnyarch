// pointer to string in r0 - if r1 is nonzero newline will be printed at the end
puts:
push(r0)
push(r2)
push(r3)
mov r2, #0x1000
.puts_loop:
ldri r3, r0, #1
cmp r3, #0
ifeq rjmp .puts_finish
str r2, r3, #0
rjmp .puts_loop
.puts_finish:
cmp r1, #0
ifnz mov r3, #0xA
ifnz str r2, r3, #0
pop(r3)
pop(r2)
pop(r0)
mov rip, lr
