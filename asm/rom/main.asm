// Funnyarch ROM
.origin 0x0
entry:
rjmp main

#include "macros.asm"
#include "hdd.asm"
#include "interrupts.asm"

#define REG_MEMSTART r24
#define REG_MEMEND r25
#define REG_MEMSIZE r26

main:
mov r0, #0b1 // set alignment flag
mtsr pcst, r0
mov r0, int_handler
or r0, r0, #0x1 // no jump table
mtsr ibptr, r0

rcall(memdetect)
mov REG_MEMSTART, r6
mov REG_MEMEND, r5
mov REG_MEMSIZE, r0
cmp REG_MEMSIZE, #0
ifeq rjmp .nomem
cmp REG_MEMSIZE, #1024
iflt rjmp .lowmem
mov rsp, REG_MEMEND // stack grows down, set stack pointer to highest memory address found

mov r0, str_boot
rcall(serial_puts)
// read the first sector
mov r0, #0
rcall(hdd_read)
// check if magic bytes match
ldr r1, r0, #0
mov r2, #0x5252
movh r2, #0x333A
cmp r1, r2
ifeq rjmp .execute_boot_code
ifneq rjmp .noboot

.execute_boot_code:
push(r0)
mov r0, str_booting
rcall(serial_puts)
pop(r0)

// copy bootsector to memory
mov r1, REG_MEMSTART
mov r2, #128 // 512 / 4
rcall(memcpy32)

mov rsp, #0 // stack pointer is invalid from this point on
mov r0, REG_MEMSTART
mov r1, REG_MEMSIZE
add rip, REG_MEMSTART, #4

.noboot:
mov r0, str_nobootmagic
rcall(serial_puts)
rjmp die

.nomem:
mov r0, str_nomem
rcall(serial_puts)
rjmp die

.lowmem:
mov r0, str_lowmem
rcall(serial_puts)
rjmp die

die:
rjmp die


// memcpy that operates in 32-bit units
// source address in r0, destination address in r1, number of bytes in r2 (must be a multiple of 4)
// trashes: r0, r1, r2, r3
memcpy32:
cmp r2, #0
ifeq rjmp .memcpy32_end
ldr r3, r0, #0
str r1, r3, #0
add r0, #4
add r1, #4
sub r2, #4
rjmp memcpy32
.memcpy32_end:
ret

// detect the amount of memory available to the system
// returns amount of memory in bytes in r0, highest memory address found in r5 and lowest memory address in r6
// trashes: r0, r1, r2, r3, r4, r5, r6
memdetect:
mov r0, #0 // r0: amount of bytes
mov r1, #0x0000 // r1: current address
mov r4, #0xFFFF // r4: max address
mov r5, #0 // r5: highest address
mov r6, #0 // r6: lowest address
.memdetect_L1:
str r1, r1, #0
ldr r3, r1, #0
cmp r1, r3
ifneq rjmp .memdetect_nomem
mov r2, #0x5555
movh r2, #0x5555
str r1, r2, #0
ldr r3, r1, #0
cmp r2, r3
ifneq rjmp .memdetect_nomem
cmp r6, #0
ifeq mov r6, r1
add r0, r0, #4
mov r5, r1
.memdetect_nomem:
add r1, r1, #4
cmp r1, r4
iflt rjmp .memdetect_L1
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


// pointer to string in r0
// trashes: r0, r1, r2, r3, r4
serial_puts:
mov r3, lr // potentioally running with no stack, so saving lr in r3
mov r2, r0
.serial_puts_L0:
ldr r0, r2, #0
mov r4, #0
.serial_puts_L1:
cmp r4, #4
ifeq rjmp .serial_puts_L0
and r1, r0,  #0xFF
cmp r1, #0
ifeq rjmp .serial_puts_end
rcall(write_serial)
shr r0, r0, #8
add r4, #1
add r2, #1
rjmp .serial_puts_L1
.serial_puts_end:
mov r0, #0x0A // newline
rcall(write_serial)
mov lr, r3
ret


str_nomem:
.string "error: No memory detected"
.align 4
str_boot:
.string "Hii hello :3"
.align 4
str_lowmem:
.string "error: too little memory to boot"
.align 4
str_nobootmagic:
.string "error: no bootsector magic bytes found"
.align 4
str_booting:
.string "loading and jumping to bootsector"
.align 4
