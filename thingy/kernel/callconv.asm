/*
 * calling convention:
 * caller saves r0-r7 (arguments)
 * callee saves: r8-r26, rfp, lr
 * args passed in: r0-r7 and then on stack (last argument is on top of stack)
 * return value in r0
 */

#define func(name) name: \
    push(lr) \
    push(rfp) \
    mov rfp, rsp

#define func_leaf(name) name: \
    push(rfp) \
    mov rfp, rsp


#define func_locals(name, localspace) name: \
    push(lr) \
    push(rfp) \
    mov rfp, rsp \
    sub rsp, #localspace


#define func_leaf_locals(name, localspace) name: \
    push(rfp) \
    mov rfp, rsp \
    sub rsp, #localspace


#define endfunc mov rsp, rfp \
    pop(rfp) \
    pop(lr) \
    ret

#define endfunc_leaf mov rsp, rfp \
    pop(rfp) \
    ret

// local offsets:
// -4 would be the first local.. -8 the second etc.
// the stack arguments start at 8 in normal functions and at 4 in leaf functions

#define getlocal(reg, offset) ldr reg, rfp, #offset

#define setlocal(reg, offset) str rfp, reg, #offset
