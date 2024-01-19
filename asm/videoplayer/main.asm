.origin 0x0
entry:
rjmp main

#include "macros.asm"

interrupt:
push(r0)
mfsr r0, pcst
shr r0, r0, #24 // interrupt number in r0
// any fault
cmp r0, #253
ifeq rjmp entry
cmp r0, #0
ifeq mov r26, #1
pop(r0)
iret

main:
mov r0, #0b1001 // alignment, hw interrupts
mtsr pcst, r0
mov r0, interrupt
or r0, r0, #0x1 // no jump table
mtsr ibptr, r0
mov rsp, #0x2200
push(lr)

// load instructions
mov r20, #0x0000
movh r20, #0xF005
.main_instrloop:
ldr r0, r20, #0
ldr r1, r20, #0
rcall(decodecmd) 
rjmp .main_instrloop

pop(lr)
rjmp entry


// command words in r0 and r1
decodecmd:
and r2, r0, #0xFF
cmp r2, #0x02
ifgt rjmp cmd_end // end loops, if we detect an invalid command simply loop
mov r3, .decodecmd_jumptable
shl r2, r2, #2
add r3, r3, r2
mov rip, r3
.decodecmd_jumptable:
rjmp cmd_newframe
rjmp cmd_fillcolor
rjmp cmd_end

cmd_newframe:
mov r26, #0
.cmd_newframe_L0:
cmp r26, #0
ifeq rjmp .cmd_newframe_L0
ret

cmd_fillcolor:
push(lr)
mov r5, #0xFFFF
movh r5, #0x0007
shr r2, r0, #8    // r2: spixels
and r2, r2, r5    // r2: spixels
shr r4, r0, #27   // r4: white
and r4, r4, #0x01 // r4: white
mov r3, r1        // r3: npixels
and r3, r3, r5    // r3: npixels

cmp r4, #0
ifneq mov r4, #0xFF

// write byte-unaligned part of pixels
and r5, r2, #0b111
shr r2, r2, #3
cmp r5, #0
ifeq rjmp .cmd_fillcolor_skipua1
// create mask
mov r6, #0x1
shl r6, r6, r5
sub r6, #1
not r6, r6
and r6, #0xFF
// read byte
mov r0, #0x0000
movh r0, #0xF000
add r0, r0, r2
push(r2)
rcall(load_byte_unaligned)
mov r8, r2
pop(r2)
// use inverted mask on byte
not r6, r6
and r8, r8, r6
not r6, r6
// set relevant bits in byte
and r7, r4, r6
or r1, r8, r7
// write byte back to fb
rcall(write_byte_unaligned)
// add 1 to start since it gets "aligned down" when not aligned to a full byte
add r2, #1
.cmd_fillcolor_skipua1:
and r5, r3, #0b111
shr r3, r3, #3
cmp r5, #0
ifeq rjmp .cmd_fillcolor_skipua2
// TODO: deduplicate code
// create mask
mov r6, #0x1
shl r6, r6, r5
sub r6, #1
// read byte
mov r0, #0x0000
movh r0, #0xF000
add r0, r0, r2
add r0, r0, r3
push(r2)
rcall(load_byte_unaligned)
mov r8, r2
pop(r2)
// use inverted mask on byte
not r6, r6
and r8, r8, r6
not r6, r6
// set relevant bits in byte
and r7, r4, r6
or r1, r8, r7
// write byte back to fb
rcall(write_byte_unaligned)
.cmd_fillcolor_skipua2:


mov r0, #0x0000
movh r0, #0xF000
add r0, r0, r2

mov r1, r4

.cmd_fillcolor_L0:
cmp r3, #0
ifeq rjmp .cmd_fillcolor_L0_end
// TODO: more efficient memset where possible
rcall(write_byte_unaligned)
add r0, #1
sub r3, #1
rjmp .cmd_fillcolor_L0

.cmd_fillcolor_L0_end:
.cmd_fillcolor_end:
pop(lr)
ret

cmd_end:
rjmp cmd_end

// address in r0
// byte to write in r1
write_byte_unaligned:
push(r0)
push(r1)
push(r2)
push(r3)
push(r4)
mov r2, #0b11 // r2 -> 0b11
and r3, r0, r2 // r3 -> misalignment of r0 (input address)
shl r3, r3, #3 // r3 -> misalignment in bits
not r2, r2 // r2 -> 0xFFFFFFFC
and r0, r0, r2 // r0 -> address aligned
ldr r2, r0, #0 // data @ r0 -> r2

and r1, r1, #0xFF // r1 & 0xFF
shl r1, r1, r3 // r1 << misalignment in bits

mov r4, #0xFF // r4 -> 0xFF
shl r4, r4, r3 // r4 << misalignment in bits
not r4, r4
and r2, r2, r4
or r2, r2, r1

str r0, r2, #0
pop(r4)
pop(r3)
pop(r2)
pop(r1)
pop(r0)
ret

// address in r0
// returns read byte in r2
load_byte_unaligned:
push(r0)
push(r1)
mov r2, #0b11 // r2 -> 0b11
and r1, r0, r2 // r1 -> misalignment of r0 (input address)
shl r1, r1, #3 // r1 -> misalignment in bits
not r2, r2 // r2 -> 0xFFFFFFFC
and r0, r0, r2 // r0 -> address aligned
ldr r2, r0, #0 // data @ r0 -> r2
shr r2, r2, r1 // r2 >> misalignment in bits
and r2, r2, #0xFF // r2 & 0xFF
pop(r1)
pop(r0)
ret
