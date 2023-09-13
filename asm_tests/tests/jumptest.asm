jumptest:
push(lr)
mov r1, #0
mov r2, #0

jmp .jumptest_1

.jumptest_4:
add r2, #99
mov rip, lr

.jumptest_3:
add r2, #5
rjal .jumptest_4
mov r3, lr
mov r4, rip
sub r4, #8
sub r2, #3
cmp r3, r4
ifneq rjmp .jumptest_failed
add r2, #1
jal .jumptest_4
mov r3, rip
mov r4, r3
sub r3, #4
sub r2, #6
cmp lr, r3
ifneq rjmp .jumptest_failed
sub r5, r4, lr
add r2, r2, r5
cmp r2, #223
ifeq rjmp .jumptest_finish
rjmp .jumptest_failed

.jumptest_2:
sub r2, #1
jmp .jumptest_3

.jumptest_1:
add r2, #25
rjmp .jumptest_2


.jumptest_failed:
add r1, #1
.jumptest_finish:
mov r0, jumptest_str
rcall(testresult)
pop(lr)
ret()

defstr(jumptest_str, "jump")
