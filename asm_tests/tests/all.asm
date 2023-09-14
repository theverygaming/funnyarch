#include "tests/cmptest.asm"
#include "tests/jumptest.asm"
#include "tests/addtest.asm"
#include "tests/subtest.asm"
#include "tests/shifttest.asm"

alltests:
push(lr)
rcall(cmptest)
rcall(jumptest)
rcall(addtest)
rcall(subtest)
rcall(shifttest)
pop(lr)
ret()
