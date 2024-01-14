#include "cpu.h"
#include <cstdio>
#include <cstring>

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
    memset(ctx->sysregs, 0, sizeof(ctx->sysregs));
}

static inline CPU_FORCEINLINE void pcst_push_state_stack(struct cpu::ctx *ctx) {
    ctx->sysregs[CPU_SYSREG_PCST] = (ctx->sysregs[CPU_SYSREG_PCST] & 0xFFFFF000) | ((ctx->sysregs[CPU_SYSREG_PCST] & 0xF0) << 4) |
                                    ((ctx->sysregs[CPU_SYSREG_PCST] & 0xF) << 4) | (ctx->sysregs[CPU_SYSREG_PCST] & 0xF);
}

static inline CPU_FORCEINLINE void pcst_pop_state_stack(struct cpu::ctx *ctx) {
    ctx->sysregs[CPU_SYSREG_PCST] = (ctx->sysregs[CPU_SYSREG_PCST] & 0xFFFFF000) | (ctx->sysregs[CPU_SYSREG_PCST] & 0xF00) |
                                    ((ctx->sysregs[CPU_SYSREG_PCST] & 0xF00) >> 4) | ((ctx->sysregs[CPU_SYSREG_PCST] & 0xF0) >> 4);
}

static inline CPU_FORCEINLINE uint32_t tlb_translate_memaddr(struct cpu::ctx *ctx, uint32_t addr) {
    return ((ctx->sysregs[CPU_SYSREG_PCST] & 0b100) != 0) ? (((ctx->tlb[(addr >> 12) & CPU_TLB_INDEX_BITS_MASK] & 0xFFFFF) << 12) | (addr & 0xFFF))
                                                          : addr;
}

static inline CPU_FORCEINLINE bool memaddr_in_tlb(struct cpu::ctx *ctx, uint32_t addr) {
    if ((ctx->sysregs[CPU_SYSREG_PCST] & 0b100) != 0) {
        uint64_t tlbent = ctx->tlb[(addr >> 12) & CPU_TLB_INDEX_BITS_MASK];
        if (((tlbent & (1ull << 40)) != 0) && (((tlbent & (0xFFFFFull << 20)) >> 20) == (addr >> 12))) {
            return true;
        }
        return false;
    }
    return true;
}

static inline CPU_FORCEINLINE void tlb_invalidate_addr(struct cpu::ctx *ctx, uint32_t addr) {
    ctx->tlb[(addr >> 12) & CPU_TLB_INDEX_BITS_MASK] = ctx->tlb[(addr >> 12) & CPU_TLB_INDEX_BITS_MASK] & ~(1ull << 40);
}

static inline CPU_FORCEINLINE void tlb_write_addr(struct cpu::ctx *ctx, uint32_t vaddr, uint32_t paddr) {
    vaddr >>= 12;
    paddr >>= 12;
    ctx->tlb[vaddr & CPU_TLB_INDEX_BITS_MASK] = paddr | ((uint64_t)vaddr << 20) | (1ull << 40);
}

static inline CPU_FORCEINLINE void do_tlbmiss(struct cpu::ctx *ctx, uint32_t addr, bool dec_rip) {
    pcst_push_state_stack(ctx);
    // save rip
    ctx->sysregs[CPU_SYSREG_TLBIRIP] = dec_rip ? (ctx->regs[CPU_REG_RIP] - 4) : ctx->regs[CPU_REG_RIP];
    ctx->sysregs[CPU_SYSREG_TLBFLT] = addr;
    // unset usermode, TLB and hardware interrupt bits
    ctx->sysregs[CPU_SYSREG_PCST] = ctx->sysregs[CPU_SYSREG_PCST] & ~0b1110ul;
    // jump
    ctx->regs[CPU_REG_RIP] = ctx->sysregs[CPU_SYSREG_TLBIPTR] & 0xFFFFFFFC;
}

static inline CPU_FORCEINLINE uint32_t interrupt(struct cpu::ctx *ctx, uint8_t n) {
    pcst_push_state_stack(ctx);
    // save rip
    ctx->sysregs[CPU_SYSREG_IRIP] = ctx->regs[CPU_REG_RIP];
    // set interrupt number in pcst
    bitset(&ctx->sysregs[CPU_SYSREG_PCST], 24, 8, (uint32_t)n);
    // unset usermode and hardware interrupt bits
    ctx->sysregs[CPU_SYSREG_PCST] = ctx->sysregs[CPU_SYSREG_PCST] & ~0b1010ul;
    // jump
    ctx->regs[CPU_REG_RIP] = (ctx->sysregs[CPU_SYSREG_IBPTR] & 0xFFFFFFFC) + (((ctx->sysregs[CPU_SYSREG_IBPTR] & 0b1) != 0) ? 0 : (4 * (uint32_t)n));
    return 4; // interrupt takes four cycles // FIXME: wrongwrongwrong!
}

void cpu::hwinterrupt(struct cpu::ctx *ctx, uint8_t n) {
    if (n > 253) {
        return;
    }
    // check hardware interrupt CPU flag
    if ((ctx->sysregs[CPU_SYSREG_PCST] & 0b1000) != 0) {
        interrupt(ctx, n);
    }
}

static inline CPU_FORCEINLINE bool shouldexecute(struct cpu::ctx *ctx, unsigned int condition) {
    switch (condition) {
    default: // always
        return true;
    case 1: // if equal
        return (ctx->regs[CPU_REG_RF] & 0b10) != 0;
    case 2: // if not equal
        return (ctx->regs[CPU_REG_RF] & 0b10) == 0;
    case 3: // if less than
        return (ctx->regs[CPU_REG_RF] & 0b01) != 0;
    case 4: // if greater than or equal
        return (ctx->regs[CPU_REG_RF] & 0b01) == 0;
    case 5: // if greater than
        return (ctx->regs[CPU_REG_RF] & 0b11) == 0;
    case 6: // if less than or equal
        return (ctx->regs[CPU_REG_RF] & 0b11) != 0;
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
    uint32_t instr;
    uint8_t opcode;
    uint8_t cond;
    if (memaddr_in_tlb(ctx, ctx->regs[CPU_REG_RIP] & 0xFFFFFFFC)) {
        instr = cpu::mem_read(ctx, tlb_translate_memaddr(ctx, ctx->regs[CPU_REG_RIP] & 0xFFFFFFFC));
    } else {
        do_tlbmiss(ctx, ctx->regs[CPU_REG_RIP] & 0xFFFFFFFC, false);
        goto finish;
    }
    ctx->regs[CPU_REG_RIP] += 4;
    opcode = instr & 0x3F;
    cond = (instr >> 6) & 0x07;

    if (!shouldexecute(ctx, cond)) {
        DEBUG_PRINTF("SKIPPING ");
        DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (ctx->regs[CPU_REG_RIP] - 4) & 0xFFFFFFFC, instr, opcode);
        clock_cycles += 3;
        goto finish;
    }

    DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (ctx->regs[CPU_REG_RIP] - 4) & 0xFFFFFFFC, instr, opcode);

    switch (opcode) {
    case 0x00: { /* NOP(E6) */
        clock_cycles += 3;
        break;
    }

    case 0x01: { /* STRPI(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->sysregs[CPU_SYSREG_PCST] & 0b1) != 0) && (((ctx->regs[e.str.tgt] + e.str.imm13) & 0b11) != 0)) {
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        if (memaddr_in_tlb(ctx, ctx->regs[e.str.tgt] + e.str.imm13)) {
            ctx->regs[e.str.tgt] += e.str.imm13;
            cpu::mem_write(ctx, tlb_translate_memaddr(ctx, ctx->regs[e.str.tgt]), ctx->regs[e.str.src]);
        } else {
            do_tlbmiss(ctx, ctx->regs[e.str.tgt] + e.str.imm13, true);
            break;
        }
        clock_cycles += 4;
        break;
    }

    case 0x02: { /* JMP(E4) */
        union enc_4<unsigned long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_RIP] = e.str.imm23 * 4;
        clock_cycles += 3;
        break;
    }

    case 0x03: { /* RJMP(E4) */
        union enc_4<long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_RIP] += e.str.imm23 * 4;
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

    case 0x05: { /* MOV(E3) MOVH(E3) */
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
        if (((ctx->sysregs[CPU_SYSREG_PCST] & 0b1) != 0) && (((ctx->regs[e.str.src] + e.str.imm13) & 0b11) != 0)) {
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        if (memaddr_in_tlb(ctx, ctx->regs[e.str.src] + e.str.imm13)) {
            ctx->regs[e.str.tgt] = cpu::mem_read(ctx, tlb_translate_memaddr(ctx, ctx->regs[e.str.src] + e.str.imm13));
        } else {
            do_tlbmiss(ctx, ctx->regs[e.str.src] + e.str.imm13, true);
            break;
        }
        clock_cycles += 5;
        break;
    }

    case 0x07: { /* LDRI(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->sysregs[CPU_SYSREG_PCST] & 0b1) != 0) && ((ctx->regs[e.str.src] & 0b11) != 0)) {
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        if (memaddr_in_tlb(ctx, ctx->regs[e.str.src])) {
            ctx->regs[e.str.tgt] = cpu::mem_read(ctx, tlb_translate_memaddr(ctx, ctx->regs[e.str.src]));
        } else {
            do_tlbmiss(ctx, ctx->regs[e.str.src], true);
            break;
        }
        ctx->regs[e.str.src] += e.str.imm13;
        clock_cycles += 5;
        break;
    }

    case 0x08: { /* STR(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->sysregs[CPU_SYSREG_PCST] & 0b1) != 0) && (((ctx->regs[e.str.tgt] + e.str.imm13) & 0b11) != 0)) {
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        if (memaddr_in_tlb(ctx, ctx->regs[e.str.tgt] + e.str.imm13)) {
            cpu::mem_write(ctx, tlb_translate_memaddr(ctx, ctx->regs[e.str.tgt] + e.str.imm13), ctx->regs[e.str.src]);
        } else {
            do_tlbmiss(ctx, ctx->regs[e.str.tgt] + e.str.imm13, true);
            break;
        }
        clock_cycles += 4;
        break;
    }

    case 0x09: { /* STRI(E2) */
        union enc_2<long> e;
        e.instr = instr;
        if (((ctx->sysregs[CPU_SYSREG_PCST] & 0b1) != 0) && ((ctx->regs[e.str.tgt] & 0b11) != 0)) {
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 254);
            break;
        }
        if (memaddr_in_tlb(ctx, ctx->regs[e.str.tgt])) {
            cpu::mem_write(ctx, tlb_translate_memaddr(ctx, ctx->regs[e.str.tgt]), ctx->regs[e.str.src]);
        } else {
            do_tlbmiss(ctx, ctx->regs[e.str.tgt], true);
            break;
        }
        ctx->regs[e.str.tgt] += e.str.imm13;
        clock_cycles += 4;
        break;
    }

    case 0x0a: { /* JAL(E4) */
        union enc_4<unsigned long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_LR] = ctx->regs[CPU_REG_RIP];
        ctx->regs[CPU_REG_RIP] = e.str.imm23 * 4;
        clock_cycles += 3;
        break;
    }

    case 0x0b: { /* RJAL(E4) */
        union enc_4<long> e;
        e.instr = instr;
        ctx->regs[CPU_REG_LR] = ctx->regs[CPU_REG_RIP];
        ctx->regs[CPU_REG_RIP] += e.str.imm23 * 4;
        clock_cycles += 3;
        break;
    }

    case 0x0c: { /* CMP(E7) */
        union enc_7 e;
        e.instr = instr;
        uint32_t result;
        bool carry = __builtin_sub_overflow(ctx->regs[e.str.tgt], ctx->regs[e.str.src], &result);
        bitset(&ctx->regs[CPU_REG_RF], 0, carry);
        bitset(&ctx->regs[CPU_REG_RF], 1, result == 0);
        clock_cycles += 4;
        break;
    }

    case 0x0d: { /* CMP(E3) */
        union enc_3<unsigned long> e;
        e.instr = instr;
        uint32_t result;
        bool carry = __builtin_sub_overflow(ctx->regs[e.str.tgt], e.str.imm16, &result);
        bitset(&ctx->regs[CPU_REG_RF], 0, carry);
        bitset(&ctx->regs[CPU_REG_RF], 1, result == 0);
        clock_cycles += 4;
        break;
    }

    case 0x0e: { /* INT(E4) */
        union enc_4<unsigned long> e;
        e.instr = instr;
        clock_cycles += 3;
        uint8_t intn = e.str.imm23 & 0xFF;
        // exceptions cannot be thrown with the int instruction
        if (intn >= 253) {
            ctx->regs[CPU_REG_RIP] -= 4;
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

    case 0x12: { /* ADD(E3) ADDH(E3) */
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

    case 0x15: { /* SUB(E3) SUBH(E3) */
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

    case 0x1E: { /* AND(E3) ANDH(E3) */
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

    case 0x21: { /* OR(E3) ORH(E3) */
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

    case 0x24: { /* XOR(E3) XORH(E3) */
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

    case 0x26: { /* MTSR(E7) MFSR(E7) */
        union enc_7 e;
        e.instr = instr;
        if ((ctx->sysregs[CPU_SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 253);
            break;
        }
        if (e.str.instr_spe == 1) { // MFSR
            if (e.str.src >= 10) {
                ctx->regs[CPU_REG_RIP] -= 4;
                clock_cycles += 3;
                clock_cycles += interrupt(ctx, 255);
                break;
            }
            ctx->regs[e.str.tgt] = ctx->sysregs[e.str.src];
        } else { // MTSR
            if (e.str.tgt >= 10) {
                ctx->regs[CPU_REG_RIP] -= 4;
                clock_cycles += 3;
                clock_cycles += interrupt(ctx, 255);
                break;
            }
            ctx->sysregs[e.str.tgt] = ctx->regs[e.str.src];
        }
        clock_cycles += 3;
        break;
    }
    case 0x27: { /* INVLPG(E5) INVLTLB(E5) */
        union enc_5 e;
        e.instr = instr;
        if ((ctx->sysregs[CPU_SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 253);
            break;
        }
        if (e.str.instr_spe == 1) { // INVLTLB
            memset(ctx->tlb, 0, sizeof(ctx->tlb[0]) * CPU_TLB_ENTRYCOUNT);
        } else { // INVLPG
            tlb_invalidate_addr(ctx, ctx->regs[e.str.tgt]);
        }
        clock_cycles += 3;
        break;
    }
    case 0x28: { /* TLBW(E1) */
        union enc_1 e;
        e.instr = instr;
        if ((ctx->sysregs[CPU_SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 253);
            break;
        }
        tlb_write_addr(ctx, ctx->regs[e.str.src1], ctx->regs[e.str.tgt]);
        clock_cycles += 3;
        break;
    }
    case 0x29: { /* IRET(E6) IRETTLB(E6) */
        union enc_6 e;
        e.instr = instr;
        if ((ctx->sysregs[CPU_SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
            ctx->regs[CPU_REG_RIP] -= 4;
            clock_cycles += 3;
            clock_cycles += interrupt(ctx, 253);
            break;
        }
        pcst_pop_state_stack(ctx);
        ctx->regs[CPU_REG_RIP] = (e.str.instr_spe == 1) ? ctx->sysregs[CPU_SYSREG_TLBIRIP] : ctx->sysregs[CPU_SYSREG_IRIP]; // IRETTLB?
        clock_cycles += 3;
        break;
    }

    default:
        INFO_PRINTF("invalid opcode! rip: 0x%x istr: 0x%x opc: 0x%x\n", (ctx->regs[CPU_REG_RIP] - 4) & 0xFFFFFFFC, instr, opcode);
        ctx->regs[CPU_REG_RIP] -= 4;
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
    "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23", "r24", "r25", "r26", "rfp", "lr",  "rsp", "rip", "rf",
};
