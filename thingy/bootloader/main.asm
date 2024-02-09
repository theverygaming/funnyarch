.origin 0x0
// magic bytes
.byte 0x52
.byte 0x52
.byte 0x3A
.byte 0x33
rjmp _entry

#include "../common/macros.asm"
#include "../common/callconv.asm"

_entry:
load_rel_addr(r2, memstart)
str r2, r0, #0
load_rel_addr(r2, memsize)
str r2, r1, #0

shr r1, r1, #2 // r1 / 4
add rsp, r0, r1 // rsp = top of memory

mov r0, #0b1 // set alignment flag
mtsr pcst, r0

mov r0, #3
load_rel_addr(r1, str_hello)
int #128

a:
load_rel_addr(r2, memstart)
ldr r0, r2, #0
load_rel_addr(r2, memsize)
ldr r0, r2, #0
rjmp a


str_hello:
.string "hello from bootloader"
.align 4

// variables
memstart:
.byte 0
.byte 0
.byte 0
.byte 0

memsize:
.byte 0
.byte 0
.byte 0
.byte 0
