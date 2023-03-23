#pragma once
#include <exception>
#include <stdint.h>

#define RAM_BYTES (128 * 1000000)
#define ROM_BYTES (1 * 1000000)
#define ROM_BASE  (0x1000)
#define RAM_BASE  (0x100000)

#define REG_IP     (32)
#define REG_SP     (33)
#define REG_FLAGS  (34)
#define REG_ISP    (35)
#define REG_SFLAGS (36)
#define REG_IVT    (37)
#define REG_PD     (38)

namespace cpu {

    class cpu_except : public std::exception {
    public:
        enum class etype { PAGEFAULT,
                           PROTECTIONFAULT,
                           INVALIDOPCODE,
                           DIVIDEBYZERO };
        cpu_except(etype);
        const char *what() const noexcept;

    private:
        etype _e;
    };

    struct cpu {
        // registers
        uint64_t regs[39]; // r0-r31, ip, sp, flags, isp, sflags, ivt, pd

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
    extern const char *regnames[39];
}
