#pragma once
#include <stdint.h>

#include "cpu.h"

namespace mem {
    template <typename T>
    inline T read_mem(uint64_t addr) {
        if ((cpu::cpuctx.regs[REG_SFLAGS] & (1 << 2)) == 0) { // no MMU
            if (addr < (RAM_BASE + RAM_BYTES) && addr >= RAM_BASE) {
                return *(T *)&cpu::cpuctx.mem_ram[addr - RAM_BASE];
            } else if (addr < (ROM_BASE + ROM_BYTES) && addr >= ROM_BASE) {
                return *(T *)&cpu::cpuctx.mem_rom[addr - ROM_BASE];
            }
            return 0;
        }
        return 0;
    }

    template <typename T>
    inline void write_mem(uint64_t addr, T val) {
        if ((cpu::cpuctx.regs[REG_SFLAGS] & (1 << 2)) == 0) { // no MMU
            if (addr < (RAM_BASE + RAM_BYTES) && addr >= RAM_BASE) {
                *(T *)&cpu::cpuctx.mem_ram[addr - RAM_BASE] = val;
            }
            return;
        }
    }
}
