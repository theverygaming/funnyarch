#include "tests/cmptest.asm"
#include "tests/jumptest.asm"
#include "tests/addtest.asm"
#include "tests/subtest.asm"
#include "tests/shifttest.asm"
#include "tests/andtest.asm"
#include "tests/ortest.asm"
#include "tests/xortest.asm"
#include "tests/nottest.asm"
#include "tests/movtest.asm"
#include "tests/regtest.asm"
#include "tests/sysregtest.asm"
#include "tests/tlbtest.asm"

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
rcall(movtest)
rcall(regtest)
rcall(sysregtest)
rcall(tlbtest)
pop(lr)
ret
