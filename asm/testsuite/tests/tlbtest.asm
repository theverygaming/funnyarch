tlbtest_int_handler:
mtsr scr0, r0
mtsr scr1, r1
mtsr scr2, r2

cmp r26, #6
ifneq rjmp .tlbtest_int_handler_error
ifeq rjmp .tlbtest_int_handler_skip

.tlbtest_int_handler_error:
mov r0, .tlbtest_failed
mtsr tlbirip, r0
mfsr r0, pcst
xor r0, #0b1000000 // unset old TLB flag
mtsr pcst, r0
rjmp .tlbtest_int_handler_end

.tlbtest_int_handler_skip:
mov r26, #5
mfsr r0, tlbirip
add r0, r0, #4
mtsr tlbirip, r0
cmp r25, #6
ifeq mfsr r0, pcst
ifeq xor r0, #0b1000000 // unset old TLB flag
ifeq mtsr pcst, r0
ifeq mov r25, #5

.tlbtest_int_handler_end:
mfsr r0, scr0
mfsr r1, scr1
mfsr r2, scr2
irettlb

tlbtest:
push(lr)
mfsr r0, pcst
push(r0)
mfsr r0, ibptr
push(r0)

mov r0, tlbtest_int_handler
or r0, r0, #0x1 // no jump table
mtsr tlbiptr, r0

mov r26, #6
mov r25, #6

// RAM & ROM identity mapping
mov r0, #0
mov r1, #0
mov r2, #0
tlbw r0, r1, r2
mov r0, #0x1000
mov r1, #0x1000
mov r2, #0
tlbw r0, r1, r2
mov r0, #0x2000
mov r1, #0x2000
mov r2, #0
tlbw r0, r1, r2

invltlb r0
mov r0, #0b100 // TLB enabled
mtsr pcst, r0
mov r0, #0x123 // this instruction should fail to execute due to missing TLB
cmp r0, #0x123
ifeq rjmp .tlbtest_failed
cmp r25, #5
ifneq rjmp .tlbtest_failed
cmp r26, #5
ifneq rjmp .tlbtest_failed

// RAM & ROM identity mapping
mov r0, #0
mov r1, #0
mov r2, #0
tlbw r0, r1, r2
mov r0, #0x1000
mov r1, #0x1000
mov r2, #0
tlbw r0, r1, r2
mov r0, #0x2000
mov r1, #0x2000
mov r2, #0
tlbw r0, r1, r2

mov r0, #0b100 // TLB enabled
mtsr pcst, r0

// access an unmapped address with all load/store instructions, expecting all to throw a TLB miss
mov r0, #0x0000
movh r0, #0xF000
mov r26, #6
str r0, r0, #0
cmp r26, #5
ifneq rjmp .tlbtest_failed
mov r26, #6
stri r0, r0, #0
cmp r26, #5
ifneq rjmp .tlbtest_failed
mov r26, #6
strpi r0, r0, #0
cmp r26, #5
ifneq rjmp .tlbtest_failed
mov r26, #6
ldr r0, r0, #0
cmp r26, #5
ifneq rjmp .tlbtest_failed
mov r26, #6
ldri r0, r0, #0
cmp r26, #5
ifneq rjmp .tlbtest_failed

// map the address
mov r1, #0x0040
movh r1, #0xF000
mov r0, #0x2000
mov r2, #0
tlbw r0, r1, r2

// write some random data to 0x2004
mov r0, #0x2004
str r0, r0, #0

// access it again, expecting everything to work fine
mov r0, #0x0004
movh r0, #0xF000
str r0, r0, #0
stri r0, r0, #0
strpi r0, r0, #0
ldr r0, r0, #0
ldri r0, r0, #0

// invalidate the TLB entry, expecting it to fail again
invlpg r0
mov r26, #6
ldri r0, r0, #0
cmp r26, #5
ifneq rjmp .tlbtest_failed

// r0 should still contain the same address
mov r1, #0x0004
movh r1, #0xF000
cmp r1, r0
ifneq rjmp .tlbtest_failed

// disable paging
mov r0, #0x0 // TLB disabled
mtsr pcst, r0

mov r0, #0x0004
movh r0, #0xF000
// 0xF0000004 should now contain different data since the TLB is disabled
ldr r1, r0, #0
cmp r1, r0
ifeq rjmp .tlbtest_failed
// 0x2004 should now contain the data we wrote to 0xF0000004
mov r2, #0x2004
ldr r1, r2, #0
cmp r1, r0
ifneq rjmp .tlbtest_failed

mov r1, #0
rjmp .tlbtest_finish

.tlbtest_failed:
mov r1, #1
.tlbtest_finish:
pop(r0)
mtsr ibptr, r0
pop(r0)
mtsr pcst, r0
mov r0, tlbtest_str
rcall(testresult)
pop(lr)
ret

defstr(tlbtest_str, "TLB")
