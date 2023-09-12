#define pushlink() strpi rsp, lr, #-4
#define poplink() ldri lr, rsp, #4

#define call(label) jal label

#define rcall(label) rjal label.rel

#define ret() mov rip, lr


mov rsp, #0x60
pushlink()
rcall(func)
rcall(func)
poplink()
jmp #0xFFFF

func:
add r1, #0x1
ret()
