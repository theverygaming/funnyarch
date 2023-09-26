#define push(reg) strpi rsp, reg, #-4
#define pop(reg) ldri reg, rsp, #4

#define call(label) jal label

#define rcall(label) rjal label

#define ret() mov rip, lr

#define defstr(name, contents) name: \
                               .string contents \
                               .byte 0 \
                               .byte 0 \
                               .byte 0

#define defstr_sm(name, contents) name: \
                               .string contents

// TODO: different tmp register
#define load_byte_unaligned(addr_reg, dst_reg) push(addr_reg) \
                                               mov dst_reg, #0b11 \
                                               and r15, addr_reg, dst_reg \
                                               shl r15, r15, #3 \ 
                                               not dst_reg, dst_reg \
                                               and addr_reg, addr_reg, dst_reg \
                                               ldri dst_reg, addr_reg, #1 \
                                               shr dst_reg, dst_reg, r15 \
                                               and dst_reg, dst_reg, #0xFF \
                                               pop(addr_reg)
