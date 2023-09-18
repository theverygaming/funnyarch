#include "tests/cmptest.asm"
#include "tests/jumptest.asm"
#include "tests/addtest.asm"
#include "tests/subtest.asm"
#include "tests/shifttest.asm"
#include "tests/andtest.asm"
#include "tests/ortest.asm"
#include "tests/xortest.asm"
#include "tests/nottest.asm"

alltests:
push(lr)
rcall(cmptest)
rcall(jumptest)
rcall(addtest)
rcall(subtest)
rcall(shifttest)
rcall(andtest)
rcall(ortest)
rcall(xortest)
rcall(nottest)
pop(lr)
ret()
