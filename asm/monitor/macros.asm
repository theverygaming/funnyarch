#define push(reg) __builtin_push(reg)
#define pop(reg) __builtin_pop(reg)

#define call(label) __builtin_call_lbl(label)

#define rcall(label) __builtin_relcall_lbl(label)

#define ret __builtin_return
