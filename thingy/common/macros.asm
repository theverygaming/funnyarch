#define push(reg) __builtin_push(reg)
#define pop(reg) __builtin_pop(reg)

#define call(label) __builtin_call_lbl(label)

#define rcall(label) __builtin_relcall_lbl(label)

#define ret __builtin_return

#define load_rel_addr(reg, label) add reg, rip, label.rel

#define load_rel_addr_long(reg, label) mov reg, label.rel \
    add reg, rip, reg \
    sub reg, #4
