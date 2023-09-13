#include "tests/cmptest.asm"
#include "tests/addtest.asm"
#include "tests/jumptest.asm"

alltests:
push(lr)
rcall(cmptest)
rcall(addtest)
rcall(jumptest)
pop(lr)
ret()
