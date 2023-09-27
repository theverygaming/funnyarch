// pointer to string in r0 - if r1 is nonzero newline will be printed at the end
puts:
push(lr)
push(r0)
push(r2)
push(r3)
push(r4)

mov r2, #0x1000
.puts_loop:
load_byte_unaligned(r0, r3, r4)
add r0, #1
cmp r3, #0
ifeq rjmp .puts_finish
push(r0)
mov r0, r3
rcall(drawchar)
pop(r0)
str r2, r3, #0
rjmp .puts_loop
.puts_finish:
cmp r1, #0
ifnz mov r3, #0xA
ifnz str r2, r3, #0
push(r0)
ifnz mov r0, r3
ifnz rjal drawchar
pop(r0)

pop(r4)
pop(r3)
pop(r2)
pop(r0)
pop(lr)
ret
