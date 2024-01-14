// read one sector from the hard drive
// sector number in r0
// returns: start of sector buffer (512 bytes) in r0
// trashes: r1, r2
hdd_read:
shl r0, r0, #3 // 31:3 - sector index
// we set the finished bit because then we can easily compare until it is set (writes to the finished bit are ignored)
or r0, #0b101 // finished, read
mov r1, #0xB004 // HDD control/status register
movh r1, #0xF004 // HDD control/status register
str r1, r0, #0

// poll until operation finished
.hdd_read_L0:
ldr r2, r1, #0
cmp r2, r0
ifneq rjmp .hdd_read_L0

mov r0, #0xB010 // HDD data buffer
movh r0, #0xF004 // HDD data buffer
ret
