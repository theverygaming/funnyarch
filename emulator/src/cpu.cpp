#include "cpu.h"
#include <stdio.h>
#include <string.h>

// #define ISDEBUG

#ifdef ISDEBUG
#define DEBUG_PRINTF(...) fprintf(stderr, __VA_ARGS__)
#else
#define DEBUG_PRINTF(...) \
    do {                  \
    } while (0)
#endif

#define INFO_PRINTF(...) fprintf(stderr, __VA_ARGS__)

template <typename T> static inline void bitset(T *c, uint8_t bit, bool value) {
    *c ^= (-value ^ *c) & (1ul << bit);
}

static inline long signexpand(unsigned long value, unsigned int bits) {
    if ((value >> (bits - 1)) != 0) {
        value |= ~((1ul << bits) - 1);
    }
    return value;
}

void cpu::init(uint32_t (*_mem_read)(uint32_t addr), void (*_mem_write)(uint32_t addr, uint32_t data)) {
    mem_read = _mem_read;
    mem_write = _mem_write;
}

void cpu::reset() {
    memset(regs, 0, sizeof(regs));
    // regs[CPU_REG_IP] = ROM_BASE;
}

bool cpu::shouldexecute(uint8_t condition) {
    switch (condition) {
    case 0: // always
        return true;
    case 1: // if equal
        return (regs[CPU_REG_FLAGS] & 0b10) != 0;
    case 2: // if not equal
        return (regs[CPU_REG_FLAGS] & 0b10) == 0;
    case 3: // if less than
        return (regs[CPU_REG_FLAGS] & 0b01) != 0;
    case 4: // if greater than or equal
        return (regs[CPU_REG_FLAGS] & 0b01) == 0;
    case 5: // if greater than
        return (regs[CPU_REG_FLAGS] & 0b11) == 0;
    case 6: // if less than or equal
        return (regs[CPU_REG_FLAGS] & 0b11) != 0;
    }
    return true;
}

union enc_1 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned int src1 : 5;
        unsigned int src2 : 5;
        unsigned int tgt : 5;
        unsigned int instr_spe : 8;
    } str;
};

union enc_2 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned int src : 5;
        unsigned int tgt : 5;
        unsigned long imm13 : 13;
    } str;
};

union enc_3 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned int tgt : 5;
        unsigned int instr_spe : 2;
        unsigned long imm16 : 16;
    } str;
};

union enc_4 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned long imm23 : 23;
    } str;
};

union enc_5 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned int tgt : 5;
        unsigned long instr_spe : 18;
    } str;
};

union enc_6 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned long instr_spe : 23;
    } str;
};

union enc_7 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned int src : 5;
        unsigned int tgt : 5;
        unsigned int instr_spe : 13;
    } str;
};

void cpu::execute(uint32_t instrs) {
begin:
    uint32_t instr = mem_read(regs[CPU_REG_IP] & 0xFFFFFFFC);
    regs[CPU_REG_IP] += 4;
    uint8_t opcode = instr & 0x3F;
    uint8_t cond = (instr >> 6) & 0x07;

    if (!shouldexecute(cond)) {
        DEBUG_PRINTF("SKIPPING ");
        DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (regs[CPU_REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);
        goto finish;
    }

    DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (regs[CPU_REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);

    switch (opcode) {
    case 0x00: { /* NOP(E6) */
        break;
    }

    case 0x01: { /* STRPI(E2) */
        union enc_2 e;
        e.instr = instr;
        regs[e.str.tgt] += signexpand(e.str.imm13, 13);
        mem_write(regs[e.str.tgt], regs[e.str.src]);
        break;
    }

    case 0x02: { /* JMP(E4) */
        union enc_4 e;
        e.instr = instr;
        regs[CPU_REG_IP] = e.str.imm23 * 4;
        break;
    }

    case 0x03: { /* RJMP(E4) */
        union enc_4 e;
        e.instr = instr;
        regs[CPU_REG_IP] += signexpand(e.str.imm23, 23) * 4;
        break;
    }

    case 0x04: { /* MOV(E7) */
        union enc_7 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src];
        break;
    }

    case 0x05: { /* MOV(E3) */
        union enc_3 e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            regs[e.str.tgt] = (regs[e.str.tgt] & 0xFFFF) | (e.str.imm16 << 16);
        } else {
            regs[e.str.tgt] = e.str.imm16;
        }
        break;
    }

    case 0x07: { /* LDRI(E2) */
        union enc_2 e;
        e.instr = instr;
        regs[e.str.tgt] = mem_read(regs[e.str.src]);
        regs[e.str.src] += signexpand(e.str.imm13, 13);
        break;
    }

    case 0x08: { /* STR(E2) */
        union enc_2 e;
        e.instr = instr;
        mem_write(regs[e.str.tgt] + signexpand(e.str.imm13, 13), regs[e.str.src]);
        break;
    }

    case 0x0a: { /* JAL(E4) */
        union enc_4 e;
        e.instr = instr;
        regs[CPU_REG_LR] = regs[CPU_REG_IP];
        regs[CPU_REG_IP] = e.str.imm23 * 4;
        break;
    }

    case 0x0b: { /* RJAL(E4) */
        union enc_4 e;
        e.instr = instr;
        regs[CPU_REG_LR] = regs[CPU_REG_IP];
        regs[CPU_REG_IP] += signexpand(e.str.imm23, 23) * 4;
        break;
    }

    case 0x0c: { /* CMP(E7) */
        union enc_7 e;
        e.instr = instr;
        uint32_t result;
        bool carry = __builtin_sub_overflow(regs[e.str.tgt], regs[e.str.src], &result);
        bitset(&regs[CPU_REG_FLAGS], 0, carry);
        bitset(&regs[CPU_REG_FLAGS], 1, result == 0);
        break;
    }

    case 0x0d: { /* CMP(E3) */
        union enc_3 e;
        e.instr = instr;
        uint32_t result;
        bool carry = __builtin_sub_overflow(regs[e.str.tgt], e.str.imm16, &result);
        bitset(&regs[CPU_REG_FLAGS], 0, carry);
        bitset(&regs[CPU_REG_FLAGS], 1, result == 0);
        break;
    }

    case 0x10: { /* ADD(E1) */
        union enc_1 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src1] + regs[e.str.src2];
        break;
    }

    case 0x11: { /* ADD(E2) */
        union enc_2 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src] + e.str.imm13;
        break;
    }

    case 0x12: { /* ADD(E3) */
        union enc_3 e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            regs[e.str.tgt] += e.str.imm16 << 16;
        } else {
            regs[e.str.tgt] += e.str.imm16;
        }
        break;
    }

    case 0x13: { /* SUB(E1) */
        union enc_1 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src1] - regs[e.str.src2];
        break;
    }

    case 0x14: { /* SUB(E2) */
        union enc_2 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src] - e.str.imm13;
        break;
    }

    case 0x15: { /* SUB(E3) */
        union enc_3 e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            regs[e.str.tgt] -= e.str.imm16 << 16;
        } else {
            regs[e.str.tgt] -= e.str.imm16;
        }
        break;
    }

    case 0x16: { /* SHL(E1) */
        union enc_1 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src2] <= 31 ? (regs[e.str.src1] << regs[e.str.src2]) : 0;
        break;
    }

    case 0x17: { /* SHL(E2) */
        union enc_2 e;
        e.instr = instr;
        regs[e.str.tgt] = e.str.imm13 <= 31 ? (regs[e.str.src] << e.str.imm13) : 0;
        break;
    }

    case 0x18: { /* SHR(E1) */
        union enc_1 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src2] <= 31 ? (regs[e.str.src1] >> regs[e.str.src2]) : 0;
        break;
    }

    case 0x19: { /* SHR(E2) */
        union enc_2 e;
        e.instr = instr;
        regs[e.str.tgt] = e.str.imm13 <= 31 ? (regs[e.str.src] >> e.str.imm13) : 0;
        break;
    }

    case 0x1A: { /* SAR(E1) */
        union enc_1 e;
        e.instr = instr;
        regs[e.str.tgt] = regs[e.str.src2] <= 31 ? ((int32_t)regs[e.str.src1] >> regs[e.str.src2]) : 0;
        break;
    }

    case 0x1B: { /* SAR(E2) */
        union enc_2 e;
        e.instr = instr;
        regs[e.str.tgt] = e.str.imm13 <= 31 ? ((int32_t)regs[e.str.src] >> e.str.imm13) : 0;
        break;
    }

    default:
        INFO_PRINTF("invalid opcode! rip: 0x%x istr: 0x%x opc: 0x%x\n", (regs[CPU_REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);
        // throw cpu_except(cpu_except::etype::INVALIDOPCODE);
    }

/*for (int i = 0; i < 32; i++) {
    printf("%s: 0x%lx | ", cpudesc::regnames[i], regs[i]);
}
printf("\n");*/
finish:
    instrs -= 1;
    if (instrs != 0) {
        goto begin;
    }
}

const char *cpudesc::regnames[32] = {
    "r0",  "r1",  "r2",  "r3",  "r4",  "r5",  "r6",  "r7",  "r8",  "r9",  "r10", "r11", "r12", "r13", "r14", "r15",
    "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23", "r24", "r25", "r26", "r27", "lr",  "rsp", "rip", "rf",
};
