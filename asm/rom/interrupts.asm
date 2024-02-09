int_handler:
mtsr scr0, lr
mtsr scr1, rf

mfsr r9, pcst
shr r9, r9, #24 // interrupt number in r9

cmp r9, #128
ifneq rjmp .int_handler_unknown
cmp r0, #4
ifgteq rjmp .int_handler_return

shl r9, r0, #2 // r0 * 4 for jump table
mov lr, .int_handler_return
mov r8, .int_handler_jumptable
add rip, r8, r9
.int_handler_jumptable:
rjmp i_diskread
rjmp i_serial_write
rjmp i_serial_read
rjmp i_serial_puts

.int_handler_unknown:
rjmp entry // unknown interrupt

.int_handler_return:

mfsr lr, scr0
mfsr rf, scr1
iret



// r1: sector number, r2: pointer to buffer
i_diskread:
mov r9, lr
mov r8, r2
mov r0, r1
rcall(hdd_read)
mov r1, r8
mov r2, #512
rcall(memcpy32)
mov lr, r9
ret

i_serial_write:
mov r9, lr
and r0, r1, #0xFF
rcall(write_serial)
mov lr, r9
ret

i_serial_read:
mov r9, lr
rcall(read_serial)
mov lr, r9
ret

i_serial_puts:
mov r9, lr
mov r0, r1
rcall(serial_puts)
mov lr, r9
ret
