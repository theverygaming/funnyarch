#include "../common/macros.asm"

.section .text
// multiplies r0 by r1 and returns in r0
// https://en.wikipedia.org/wiki/Ancient_Egyptian_multiplication#Russian_peasant_multiplication
__libsupport_mult:
  mov r2, #0
.__libsupport_mult_L0:
  cmp r0, #0
  ifeq rjmp .__libsupport_mult_end
  and r3, r0, #0x1
  cmp r3, #0
  ifneq add r2, r2, r1
  shr r0, r0, #1
  shl r1, r1, #1
  rjmp .__libsupport_mult_L0
.__libsupport_mult_end:
  mov r0, r2
  ret
