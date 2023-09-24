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
