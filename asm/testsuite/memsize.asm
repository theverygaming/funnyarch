memsize:
.regalias r0 begin_addr
.regalias r1 current_addr
.regalias r2 saved_data
.regalias r3 tmp1
.regalias r4 end_addr
.regalias r10 total_mem_bytes
mov begin_addr, #0x1000 // begin address
mov end_addr, #0xFFFF // end address
mov total_mem_bytes, #0
mov current_addr, begin_addr
.memsize_loop:
ldr saved_data, current_addr, #0 // saved_data contains data @current_addr
str current_addr, current_addr, #0 // store current address @current_addr
ldr tmp1, current_addr, #0 // tmp1 contains data @current_addr
cmp tmp1, current_addr
ifeq add total_mem_bytes, #4
stri current_addr, saved_data, #4 // restore old data
cmp current_addr, end_addr
iflt rjmp .memsize_loop
ret
.regaliasclear
