#pragma once
#include <stdint.h>

#include "cpu.h"
#include "mmio.h"

namespace mem {

    // why? It makes things a _lot_ easier + compiler should be able to optimize it away
    inline uint8_t read_byte(uint64_t paddr) {
        if ((paddr & ((uint64_t)1 << 63)) != 0) { // MMIO
            return mmio::read(paddr & (~((uint64_t)1 << 63)));
        }
        if (paddr < (RAM_BASE + RAM_BYTES) && paddr >= RAM_BASE) {
            return cpu::cpuctx.mem_ram[paddr - RAM_BASE];
        }
        if (paddr < (ROM_BASE + ROM_BYTES) && paddr >= ROM_BASE) {
            return cpu::cpuctx.mem_rom[paddr - ROM_BASE];
        }
        return rand(); // read from an address that is not mapped to anything would result in a trash value on real hw
    }

    inline void write_byte(uint64_t paddr, uint8_t value) {
        if ((paddr & ((uint64_t)1 << 63)) != 0) { // MMIO
            mmio::write(paddr & (~((uint64_t)1 << 63)), value);
            return;
        }
        if (paddr < (RAM_BASE + RAM_BYTES) && paddr >= RAM_BASE) {
            cpu::cpuctx.mem_ram[paddr - RAM_BASE] = value;
        }
    }

    template <typename T>
    inline T read(uint64_t addr) {
        uint64_t val_u64 = 0;
        if ((cpu::cpuctx.regs[REG_SFLAGS] & (1 << 2)) == 0) { // no MMU
            for (int i = 0; i < sizeof(T); i++) {
                val_u64 |= (uint64_t)read_byte(addr + i) << (i * 8);
            }
        }
        return (T)val_u64;
    }

    template <typename T>
    inline void write(uint64_t addr, T val) {
        uint64_t val_u64 = (uint64_t)val;
        if ((cpu::cpuctx.regs[REG_SFLAGS] & (1 << 2)) == 0) { // no MMU
            for (int i = 0; i < sizeof(T); i++) {
                write_byte(addr + i, (val_u64 >> (i * 8)) & 0xFF);
            }
        }
    }
}
