.section .entry
// magic bytes
.byte 0x52
.byte 0x52
.byte 0x3A
.byte 0x33
rjmp _entry

#include "../common/macros.asm"
#include "../common/callconv.asm"

.section .text
_entry:
shr r1, r1, #2 // r1 / 4
add rsp, r0, r1 // rsp = top of memory

mov r0, #0b1 // set alignment flag
mtsr pcst, r0
mov r0, #0 // int_handler
or r0, r0, #0x1 // no jump table
mtsr ibptr, r0

rjal kmain
// jump to ROM start, hopefully resetting the machine
jmp #0
