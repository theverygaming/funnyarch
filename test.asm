#define pushlink() strpi rsp, lr, #-4
#define poplink() ldri lr, rsp, #4

#define call(label) jal label

#define rcall(label) rjal label.rel

#define ret() mov rip, lr


mov rsp, #0x2708
pushlink()
rcall(func)
mov r1, nodivstring
rcall(puts)
poplink()
jmp #0xFFFF

func:
pushlink()
add r1, #0x1
poplink()
ret()

fillstack:
sub r1, #0x1
strpi rsp, r1, #-4
rjmp fillstack.rel

puts:
mov r2, #0x1000
ldri r3, r1, #4
str r2, r3, #0
rjmp puts.rel

nodivstring:
.string "Hello world!!!"
