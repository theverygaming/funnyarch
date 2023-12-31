// Monitor program
// Inspired by the Apple I Wozniak Monitor
.origin 0x0
entry:
rjmp main

#include "macros.asm"

#define LINE_BUFFER_BEGIN 0x2100
#define LINE_BUFFER_END 0x2140

// r10 = current memory location
// r11 = next memory location

main:
mov r0, #0b1 // set alignment flag
mtsr pcst, r0
mov r0, entry
or r0, r0, #0x1 // no jump table
mtsr ibptr, r0
push(lr)
mov rsp, #0x2100
mov r0, #0x5C // '\'
rcall(write_serial)
mov r0, #0x0A // newline
rcall(write_serial)
pop(lr)

mov r10, #0
mov r11, #0

procloop:
push(lr)
rcall(readline)
mov r0, #LINE_BUFFER_BEGIN
_procloop_continue_reading_line:
mov r3, r0
rcall(buffer_atoi)
cmp r0, r3
ifneq mov r10, r1
ifneq rjmp _procloop_next_read
rcall(load_byte_unaligned)
cmp r2, #0x0A // newline
ifeq rjmp _procloop_end
add r0, #1
rjmp _procloop_continue_reading_line

_procloop_next_read:
rcall(load_byte_unaligned)
cmp r2, #0x0A // newline
ifeq mov r11, r10
ifeq rjmp _procloop_do_xam
cmp r2, #0x52 // 'R'
ifeq mov rip, r10
cmp r2, #0x3A // ':'
ifeq add r0, #1
ifeq rjmp _procloop_do_write
cmp r2, #0x2E // '.'
ifneq mov r11, r10
ifneq rjmp _procloop_do_xam

add r0, #1
rcall(buffer_atoi)
mov r11, r1
rjmp _procloop_do_xam

_procloop_do_write:
mov r3, r0
rcall(buffer_atoi)
cmp r0, r3
ifeq rjmp _procloop_do_write_checkchar

push(r0)
push(r1)
push(r10)
mov r11, r10
rcall(mode_xam_multi)
pop(r10)
pop(r1)
mov r0, r10
rcall(write_byte_unaligned)
pop(r0)

add r10, #1

_procloop_do_write_checkchar:
rcall(load_byte_unaligned)
cmp r2, #0x20 // ' '
ifeq add r0, #1
ifeq rjmp _procloop_do_write
ifneq rjmp _procloop_continue_reading_line

_procloop_do_xam:
push(r0)
rcall(mode_xam_multi)
pop(r0)

rcall(load_byte_unaligned)
cmp r2, #0x0A // newline
ifneq add r0, #1
ifneq rjmp _procloop_continue_reading_line

_procloop_end:
pop(lr)
rjmp procloop

mode_xam_multi:
push(lr)
_xam_multi_loop_reprint_addr:
mov r3, #0 // r3 holds the amount of bytes printed (to wrap lines)
cmp r10, r11 // check if we have examined enough
ifgt rjmp _xam_multi_end
mov r0, r10
mov r1, #7
rcall(itoa)
mov r0, #0x3A // ':'
rcall(write_serial)
_xam_multi_loop:
cmp r10, r11 // check if we have examined enough
ifgt rjmp _xam_multi_end
mov r0, #0x20 // ' '
rcall(write_serial)

mov r0, r10
rcall(load_byte_unaligned)
mov r0, r2
mov r1, #1
rcall(itoa)

add r10, #1
add r3, #1 // r3 holds the amount of bytes printed (to wrap lines)
cmp r3, #8
iflt rjmp _xam_multi_loop
cmp r10, r11 // check if we have examined enough
ifgt rjmp _xam_multi_end
mov r0, #0x0A // newline
rcall(write_serial)
rjmp _xam_multi_loop_reprint_addr

_xam_multi_end:
mov r0, #0x0A // newline
rcall(write_serial)
pop(lr)
ret

// takes number from r0 and prints it to serial as hex
// r1 contains the number of nibbles to print subtracted by one
// trashes: r1, r2
itoa:
shl r2, r1, #2 // r2 = r1 * 4
shr r2, r0, r2 // r2 = r0 >> r2
and r2, r2, #0x0F // r2 = r2 & 0x0F

cmp r2, #10
iflt add r2, #0x30 // '0'
ifgteq add r2, #0x37 // 'A'-10

push(r0)
push(r1)
push(lr)
mov r0, r2
rcall(write_serial)
pop(lr)
pop(r1)
pop(r0)

sub r1, #1
cmp r1, #7
iflt rjmp itoa
ret


// reads hex number from buffer (only uppercase letters supported). Returns on first unexpected character
// r0: buffer address & address of unexpected character on return
// r1: number read
// trashes: r2
buffer_atoi:
mov r1, #0
_buffer_atoi_loop:
push(lr)
rcall(load_byte_unaligned)
pop(lr)
and r2, #0xFF

cmp r2, #0x30 // '0'
iflt rjmp _buffer_atoi_letter
cmp r2, #0x39 // '9'
ifgt rjmp _buffer_atoi_letter
sub r2, #0x30
rjmp _buffer_atoi_mul

_buffer_atoi_letter:
cmp r2, #0x41 // 'A'
iflt rjmp _buffer_atoi_exit
cmp r2, #0x46 // 'F'
ifgt rjmp _buffer_atoi_exit
sub r2, #0x37

_buffer_atoi_mul:
shl r1, r1, #4 // r1 = r1 * 16
add r1, r1, r2

add r0, #1
rjmp _buffer_atoi_loop
_buffer_atoi_exit:
ret


// reads from serial until line break
// trashes: r0, r1, r2
readline:
push(lr)
mov r2, #LINE_BUFFER_BEGIN
_readline_loop:

rcall(read_serial)
push(r0)
mov r1, r0
mov r0, r2
rcall(write_byte_unaligned)
pop(r0)

cmp r0, #0x0A // newline
ifeq rjal write_serial
ifeq rjmp _readline_end
cmp r0, #0x08 // backspace
ifeq rjmp _readline_backspace
rcall(write_serial)

add r2, #1
cmp r2, #LINE_BUFFER_END
ifgteq mov r2, #LINE_BUFFER_BEGIN
rjmp _readline_loop
_readline_backspace:
cmp r2, #LINE_BUFFER_BEGIN
ifgt sub r2, #1
ifgt rjal write_serial
rjmp _readline_loop
_readline_end:
pop(lr)
ret


// character read in r0
read_serial:
mov r0, #0xB000
movh r0, #0xF004
ldr r0, r0, #0
cmp r0, #0
ifz rjmp read_serial
and r0, r0, #0xFF
ret


// character to write in r0
// trashes: r1
write_serial:
mov r1, #0xB000
movh r1, #0xF004
str r1, r0, #0
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
