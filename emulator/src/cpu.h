#pragma once
#include <exception>
#include <stdint.h>

#define RAM_BYTES (128 * 1000000)
#define ROM_BYTES (1 * 8192)
#define ROM_BASE  (0)
#define RAM_BASE  (0x2000)

#define REG_LR    (28)
#define REG_SP    (29)
#define REG_IP    (30)
#define REG_FLAGS (31)

namespace cpu {

    class cpu_except : public std::exception {
    public:
        enum class etype { PAGEFAULT, PROTECTIONFAULT, INVALIDOPCODE, DIVIDEBYZERO };
        cpu_except(etype);
        const char *what() const noexcept;

    private:
        etype _e;
    };

    struct cpu {
        // registers
        uint32_t regs[32];

        uint8_t *mem_ram;
        const uint8_t *mem_rom;
    };

    extern struct cpu cpuctx;

    void init();
    void deinit();
    void reset();

    void execute();
}

namespace cpudesc {
    extern const char *regnames[32];
}
