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
add rsp, r0, r1
sub rsp, rsp, #4 // rsp = top of memory
// save r0 and r1 on the stack
push(r0)
push(r1)

mov r2, #0b1 // set alignment flag
mtsr pcst, r2

// read as many sectors of HDD as we can! only the first sector isn't enough
// r11 = max. available sectors
mov r11, #0xB008
movh r11, #0xF004
ldr r11, r11, #0
mov r12, #0x03
shl r12, r12, #29
not r12, r12
and r11, r11, r12

// r10 = current sector
mov r10, #1

// r12 = current memory address
add r12, r0, #512

// r13 = max memory address
add r13, r0, r1
// leave 1KiB of space for stack and stuff
sub r13, r13, #1024

.hdd_read_sectors:
// have we reached the end of the drive?
cmp r10, r11
ifgteq rjmp .hdd_read_sectors_end
// have we reached the end of memory?
cmp r12, r13
ifgteq rjmp .hdd_read_sectors_end
// debug print
mov r0, #1
mov r1, #82 // 'R'
int #128
// read the sector
mov r0, #0 // function = read sector from disk
mov r1, r10 // sector number
mov r2, r12 // memory address
int #128
// increment sector & memory counters
add r10, r10, #1
add r12, r12, #512
rjmp .hdd_read_sectors
.hdd_read_sectors_end:

// debug print
mov r0, #1
mov r1, #69 // 'E'
int #128

rjal kmain
// jump to ROM start, hopefully resetting the machine
jmp #0
