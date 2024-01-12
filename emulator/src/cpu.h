#pragma once
#include <cstddef>
#include <cstdint>

#define CPU_REG_LR         (28)
#define CPU_REG_RIP        (30)
#define CPU_REG_RF         (31)
#define CPU_SYSREG_IRIP    (4)
#define CPU_SYSREG_IBPTR   (5)
#define CPU_SYSREG_PCST    (6)
#define CPU_SYSREG_TLBIRIP (7)
#define CPU_SYSREG_TLBIPTR (8)
#define CPU_SYSREG_TLBFLT  (9)

#define CPU_TLB_INDEX_BITS      (7ull)
#define CPU_TLB_ENTRYCOUNT      (1ull << CPU_TLB_INDEX_BITS)
#define CPU_TLB_INDEX_BITS_MASK ((1ull << CPU_TLB_INDEX_BITS) - 1)

namespace cpu {
    struct ctx {
        uint32_t regs[32];
        uint32_t sysregs[10];
        uint64_t tlb[CPU_TLB_ENTRYCOUNT]; // [19:0] bits 12-31 of physical address, [39:20] bits 12-31 of virtual address, [40] active bit
        uint32_t (*mem_read_ptr)(uint32_t addr);
        void (*mem_write_ptr)(uint32_t addr, uint32_t data);
    };

    void init(struct ctx *ctx);
    void reset(struct ctx *ctx);
    uint32_t execute(struct ctx *ctx, uint32_t instrs);
    void hwinterrupt(struct ctx *ctx, uint8_t n);

    inline __attribute__((always_inline)) uint32_t mem_read(struct ctx *ctx, uint32_t addr) {
        return ctx->mem_read_ptr(addr);
    }

    inline __attribute__((always_inline)) void mem_write(struct ctx *ctx, uint32_t addr, uint32_t data) {
        return ctx->mem_write_ptr(addr, data);
    }
}

namespace cpudesc {
    extern const char *regnames[32];
}
