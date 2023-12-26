#include "cpu.h"
#include <stdio.h>
#include <string.h>

#define CPU_FORCEINLINE __attribute__((always_inline))

// #define ISDEBUG

#ifdef ISDEBUG
#define DEBUG_PRINTF(...) fprintf(stderr, __VA_ARGS__)
#else
#define DEBUG_PRINTF(...) \
    do {                  \
    } while (0)
#endif

#define INFO_PRINTF(...) fprintf(stderr, __VA_ARGS__)

template <typename T> static inline CPU_FORCEINLINE void bitset(T *c, uint8_t bit, bool value) {
    *c ^= (-value ^ *c) & (1ul << bit);
}

template <typename T> static inline CPU_FORCEINLINE void bitset(T *c, uint8_t bits_start, uint8_t bits_len, T value) {
    T mask = (1ul << bits_len) - 1;
    T mask_shifted = mask << bits_start;
    *c = (*c & (~mask_shifted)) | ((value & mask) << bits_start);
}

void cpu::init(struct cpu::ctx *ctx) {
    cpu::reset(ctx);
}

void cpu::reset(struct cpu::ctx *ctx) {
    memset(ctx->regs, 0, sizeof(ctx->regs));
}

static inline CPU_FORCEINLINE uint32_t interrupt(struct cpu::ctx *ctx, uint8_t n) {
    // push rip
    ctx->regs[CPU_REG_SP] -= 4;
    cpu::mem_write(ctx, ctx->regs[CPU_REG_SP], ctx->regs[CPU_REG_IP]);
    // push flags
    ctx->regs[CPU_REG_SP] -= 4;
    cpu::mem_write(ctx, ctx->regs[CPU_REG_SP], ctx->regs[CPU_REG_FLAGS]);
    // set interrupt number in flags
    bitset(&ctx->regs[CPU_REG_FLAGS], 24, 8, (uint32_t)n);
    // jump
    ctx->regs[CPU_REG_IP] = ctx->regs[CPU_REG_IPTR] & 0xFFFFFFFC;
    return 4; // interrupt takes four cycles
}

static inline CPU_FORCEINLINE bool shouldexecute(struct cpu::ctx *ctx, unsigned int condition) {
    switch (condition) {
    default: // always
        return true;
    case 1: // if equal
        return (ctx->regs[CPU_REG_FLAGS] & 0b10) != 0;
    case 2: // if not equal
        return (ctx->regs[CPU_REG_FLAGS] & 0b10) == 0;
    case 3: // if less than
        return (ctx->regs[CPU_REG_FLAGS] & 0b01) != 0;
    case 4: // if greater than or equal
        return (ctx->regs[CPU_REG_FLAGS] & 0b01) == 0;
    case 5: // if greater than
        return (ctx->regs[CPU_REG_FLAGS] & 0b11) == 0;
    case 6: // if less than or equal
        return (ctx->regs[CPU_REG_FLAGS] & 0b11) != 0;
    }
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

template <typename immtype> union enc_2 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned int src : 5;
        unsigned int tgt : 5;
        immtype imm13 : 13;
    } str;
};

template <typename immtype> union enc_3 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        unsigned int tgt : 5;
        unsigned int instr_spe : 2;
        immtype imm16 : 16;
    } str;
};

template <typename immtype> union enc_4 {
    uint32_t instr;
    struct __attribute__((packed)) {
        unsigned int opcode : 6;
        unsigned int condition : 3;
        immtype imm23 : 23;
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

uint32_t cpu::execute(struct cpu::ctx *ctx, uint32_t instrs) {
    uint32_t clock_cycles = 0;
begin:
    uint32_t instr = cpu::mem_read(ctx, ctx->regs[CPU_REG_IP] & 0xFFFFFFFC);
    ctx->regs[CPU_REG_IP] += 4;
    uint8_t opcode = instr & 0x3F;
    uint8_t cond = (instr >> 6) & 0x07;

    if (!shouldexecute(ctx, cond)) {
        DEBUG_PRINTF("SKIPPING ");
        DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (ctx->regs[CPU_REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);
        clock_cycles += 3;
        goto finish;
    }

    DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (ctx->regs[CPU_REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);

    switch (opcode) {
    case 0x00: { /* NOP(E6) */
        clock_cycles += 3;
        break;
    }

    case 0x01: { /* STRPI(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->regs[31] & 0b100) != 0) && (((ctx->regs[e.str.tgt] + e.str.imm13) & 0b11) != 0)) {
            ctx->regs[CPU_REG_IP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        ctx->regs[e.str.tgt] += e.str.imm13;
        cpu::mem_write(ctx, ctx->regs[e.str.tgt], ctx->regs[e.str.src]);
        clock_cycles += 4;
        break;
    }

    case 0x02: { /* JMP(E4) */
        union enc_4<unsigned long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_IP] = e.str.imm23 * 4;
        clock_cycles += 3;
        break;
    }

    case 0x03: { /* RJMP(E4) */
        union enc_4<long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_IP] += e.str.imm23 * 4;
        clock_cycles += 3;
        break;
    }

    case 0x04: { /* MOV(E7) */
        union enc_7 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src];
        clock_cycles += 3;
        break;
    }

    case 0x05: { /* MOV(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            ctx->regs[e.str.tgt] = (ctx->regs[e.str.tgt] & 0xFFFF) | (e.str.imm16 << 16);
        } else {
            ctx->regs[e.str.tgt] = e.str.imm16;
        }
        clock_cycles += 3;
        break;
    }

    case 0x06: { /* LDR(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->regs[31] & 0b100) != 0) && (((ctx->regs[e.str.src] + e.str.imm13) & 0b11) != 0)) {
            ctx->regs[CPU_REG_IP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        ctx->regs[e.str.tgt] = cpu::mem_read(ctx, ctx->regs[e.str.src] + e.str.imm13);
        clock_cycles += 5;
        break;
    }

    case 0x07: { /* LDRI(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->regs[31] & 0b100) != 0) && ((ctx->regs[e.str.src] & 0b11) != 0)) {
            ctx->regs[CPU_REG_IP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        ctx->regs[e.str.tgt] = cpu::mem_read(ctx, ctx->regs[e.str.src]);
        ctx->regs[e.str.src] += e.str.imm13;
        clock_cycles += 5;
        break;
    }

    case 0x08: { /* STR(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->regs[31] & 0b100) != 0) && (((ctx->regs[e.str.tgt] + e.str.imm13) & 0b11) != 0)) {
            ctx->regs[CPU_REG_IP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        cpu::mem_write(ctx, ctx->regs[e.str.tgt] + e.str.imm13, ctx->regs[e.str.src]);
        clock_cycles += 4;
        break;
    }

    case 0x09: { /* STRI(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->regs[31] & 0b100) != 0) && ((ctx->regs[e.str.tgt] & 0b11) != 0)) {
            ctx->regs[CPU_REG_IP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        cpu::mem_write(ctx, ctx->regs[e.str.tgt], ctx->regs[e.str.src]);
        ctx->regs[e.str.tgt] += e.str.imm13;
        clock_cycles += 4;
        break;
    }

    case 0x0a: { /* JAL(E4) */
        union enc_4<unsigned long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_LR] = ctx->regs[CPU_REG_IP];
        ctx->regs[CPU_REG_IP] = e.str.imm23 * 4;
        clock_cycles += 3;
        break;
    }

    case 0x0b: { /* RJAL(E4) */
        union enc_4<long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_LR] = ctx->regs[CPU_REG_IP];
        ctx->regs[CPU_REG_IP] += e.str.imm23 * 4;
        clock_cycles += 3;
        break;
    }

    case 0x0c: { /* CMP(E7) */
        union enc_7 e;
        e.instr = instr;
        uint32_t result;
        bool carry = __builtin_sub_overflow(ctx->regs[e.str.tgt], ctx->regs[e.str.src], &result);
        bitset(&ctx->regs[CPU_REG_FLAGS], 0, carry);
        bitset(&ctx->regs[CPU_REG_FLAGS], 1, result == 0);
        clock_cycles += 4;
        break;
    }

    case 0x0d: { /* CMP(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        uint32_t result;
        bool carry = __builtin_sub_overflow(ctx->regs[e.str.tgt], e.str.imm16, &result);
        bitset(&ctx->regs[CPU_REG_FLAGS], 0, carry);
        bitset(&ctx->regs[CPU_REG_FLAGS], 1, result == 0);
        clock_cycles += 4;
        break;
    }

    case 0x0e: { /* INT(E4) */
        union enc_4<unsigned long> e;
        e.instr = instr;
        clock_cycles += 3;
        uint8_t intn = e.str.imm23 & 0xFF;
        // exceptions cannot be thrown with the int instruction
        if (intn >= 254) {
            ctx->regs[CPU_REG_IP] -= 4;
            intn = 255;
        }
        clock_cycles += interrupt(ctx, intn);
        break;
    }

    case 0x10: { /* ADD(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src1] + ctx->regs[e.str.src2];
        clock_cycles += 4;
        break;
    }

    case 0x11: { /* ADD(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src] + e.str.imm13;
        clock_cycles += 4;
        break;
    }

    case 0x12: { /* ADD(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            ctx->regs[e.str.tgt] += e.str.imm16 << 16;
        } else {
            ctx->regs[e.str.tgt] += e.str.imm16;
        }
        clock_cycles += 4;
        break;
    }

    case 0x13: { /* SUB(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src1] - ctx->regs[e.str.src2];
        clock_cycles += 4;
        break;
    }

    case 0x14: { /* SUB(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src] - e.str.imm13;
        clock_cycles += 4;
        break;
    }

    case 0x15: { /* SUB(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            ctx->regs[e.str.tgt] -= e.str.imm16 << 16;
        } else {
            ctx->regs[e.str.tgt] -= e.str.imm16;
        }
        clock_cycles += 4;
        break;
    }

    case 0x16: { /* SHL(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src1] << (ctx->regs[e.str.src2] & 0b11111);
        clock_cycles += 4;
        break;
    }

    case 0x17: { /* SHL(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src] << (e.str.imm13 & 0b11111);
        clock_cycles += 4;
        break;
    }

    case 0x18: { /* SHR(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src1] >> (ctx->regs[e.str.src2] & 0b11111);
        clock_cycles += 4;
        break;
    }

    case 0x19: { /* SHR(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src] >> (e.str.imm13 & 0b11111);
        clock_cycles += 4;
        break;
    }

    case 0x1A: { /* SAR(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = (int32_t)ctx->regs[e.str.src1] >> (ctx->regs[e.str.src2] & 0b11111);
        clock_cycles += 4;
        break;
    }

    case 0x1B: { /* SAR(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = (int32_t)ctx->regs[e.str.src] >> (e.str.imm13 & 0b11111);
        clock_cycles += 4;
        break;
    }

    case 0x1C: { /* AND(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src1] & ctx->regs[e.str.src2];
        clock_cycles += 4;
        break;
    }

    case 0x1D: { /* AND(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src] & e.str.imm13;
        clock_cycles += 4;
        break;
    }

    case 0x1E: { /* AND(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            ctx->regs[e.str.tgt] &= e.str.imm16 << 16;
        } else {
            ctx->regs[e.str.tgt] &= e.str.imm16;
        }
        clock_cycles += 4;
        break;
    }

    case 0x1F: { /* OR(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src1] | ctx->regs[e.str.src2];
        clock_cycles += 4;
        break;
    }

    case 0x20: { /* OR(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src] | e.str.imm13;
        clock_cycles += 4;
        break;
    }

    case 0x21: { /* OR(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            ctx->regs[e.str.tgt] |= e.str.imm16 << 16;
        } else {
            ctx->regs[e.str.tgt] |= e.str.imm16;
        }
        clock_cycles += 4;
        break;
    }

    case 0x22: { /* XOR(E1) */
        union enc_1 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src1] ^ ctx->regs[e.str.src2];
        clock_cycles += 4;
        break;
    }

    case 0x23: { /* XOR(E2) */
        union enc_2<unsigned long> e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ctx->regs[e.str.src] ^ e.str.imm13;
        clock_cycles += 4;
        break;
    }

    case 0x24: { /* XOR(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        if (e.str.instr_spe == 0b01) {
            ctx->regs[e.str.tgt] ^= e.str.imm16 << 16;
        } else {
            ctx->regs[e.str.tgt] ^= e.str.imm16;
        }
        clock_cycles += 4;
        break;
    }

    case 0x25: { /* NOT(E7) */
        union enc_7 e;
        e.instr = instr;
        ctx->regs[e.str.tgt] = ~ctx->regs[e.str.src];
        clock_cycles += 4;
        break;
    }

    default:
        INFO_PRINTF("invalid opcode! rip: 0x%x istr: 0x%x opc: 0x%x\n", (ctx->regs[CPU_REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);
        ctx->regs[CPU_REG_IP] -= 4;
        clock_cycles += 3;
        clock_cycles += interrupt(ctx, 255);
        // throw cpu_except(cpu_except::etype::INVALIDOPCODE);
    }
finish:
    if (--instrs != 0) {
        goto begin;
    }
    return clock_cycles;
}

const char *cpudesc::regnames[32] = {
    "r0",  "r1",  "r2",  "r3",  "r4",  "r5",  "r6",  "r7",  "r8",  "r9",  "r10", "r11",  "r12", "r13", "r14", "r15",
    "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23", "r24", "r25", "rfp", "iptr", "lr",  "rsp", "rip", "rf",
};
