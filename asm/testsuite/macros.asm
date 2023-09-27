#define push(reg) __builtin_push(reg)
#define pop(reg) __builtin_pop(reg)

#define call(label) __builtin_call_lbl(label)

#define rcall(label) __builtin_relcall_lbl(label)

#define ret __builtin_return

#define defstr(name, contents) name: \
                               .string contents \
                               .byte 0 \
                               .byte 0 \
                               .byte 0

#define defstr_sm(name, contents) name: \
                               .string contents

#define load_byte_unaligned(addr_reg, dst_reg, tmp_reg) push(addr_reg) \
                                               mov dst_reg, #0b11 \
                                               and tmp_reg, addr_reg, dst_reg \
                                               shl tmp_reg, tmp_reg, #3 \
                                               not dst_reg, dst_reg \
                                               and addr_reg, addr_reg, dst_reg \
                                               ldri dst_reg, addr_reg, #1 \
                                               shr dst_reg, dst_reg, tmp_reg \
                                               and dst_reg, dst_reg, #0xFF \
                                               pop(addr_reg)
