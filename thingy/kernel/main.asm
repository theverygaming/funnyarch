.origin 0x0
// magic bytes
.byte 0x52
.byte 0x52
.byte 0x3A
.byte 0x33
rjmp _entry

#include "../common/macros.asm"
#include "../common/callconv.asm"
#include "switch.asm"

#define PROC_PTR #0x2000

_entry:
shr r1, r1, #2 // r1 / 4
add rsp, r0, r1 // rsp = top of memory

// set up stack for second process
load_rel_addr(r0, y)
sub rsp, #100
push(r0)
sub rsp, #80
mov r0, PROC_PTR
str r0, rsp, #0
add rsp, #184

mov r0, #0b1 // set alignment flag
mtsr pcst, r0
mov r0, #0 // int_handler
or r0, r0, #0x1 // no jump table
mtsr ibptr, r0

a:
rjmp x_l
rjmp a


func(x)
x_l:
// Serial data register
mov r0, #0xB000
movh r0, #0xF004

mov r1, #0x48 // 'H'
str r0, r1, #0
mov r1, #0x69 // 'i'
str r0, r1, #0
mov r1, #0x21 // '!'
str r0, r1, #0
mov r1, #0x0A // '\n'
str r0, r1, #0

mov r0, PROC_PTR
ldr r1, r0, #0
rcall(switch)

rjmp x_l
endfunc

func(y)
y_l:
// Serial data register
mov r0, #0xB000
movh r0, #0xF004

mov r1, #0x3A // ':'
str r0, r1, #0
mov r1, #0x33 // '3'
str r0, r1, #0
mov r1, #0x0A // '\n'
str r0, r1, #0

mov r0, PROC_PTR
ldr r1, r0, #0
rcall(switch)

rjmp y_l
endfunc
