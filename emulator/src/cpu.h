#pragma once
#include <cstddef>
#include <cstdint>

#define CPU_REG_IPTR  (27)
#define CPU_REG_LR    (28)
#define CPU_REG_SP    (29)
#define CPU_REG_IP    (30)
#define CPU_REG_FLAGS (31)

namespace cpu {
    struct ctx {
        uint32_t regs[32];
        uint32_t (*mem_read_ptr)(uint32_t addr);
        void (*mem_write_ptr)(uint32_t addr, uint32_t data);
    };

    void init(struct ctx *ctx);
    void reset(struct ctx *ctx);
    uint32_t execute(struct ctx *ctx, uint32_t instrs);

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
