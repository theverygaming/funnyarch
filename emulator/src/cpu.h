#pragma once
#include <cstddef>
#include <cstdint>

#define CPU_REG_LR    (28)
#define CPU_REG_SP    (29)
#define CPU_REG_IP    (30)
#define CPU_REG_FLAGS (31)

class cpu {
public:
    void init(uint32_t (*mem_read)(uint32_t addr), void (*mem_write)(uint32_t addr, uint32_t data));
    void reset();

    uint32_t execute(uint32_t instrs);

    uint32_t regs[32];

private:
    uint32_t (*mem_read)(uint32_t addr) = nullptr;
    void (*mem_write)(uint32_t addr, uint32_t data) = nullptr;
};

namespace cpudesc {
    extern const char *regnames[32];
}
