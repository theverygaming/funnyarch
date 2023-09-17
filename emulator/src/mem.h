#pragma once
#include <cstdint>

#include "cpu.h"
#include "mmio.h"

#define RAM_BYTES (4096)
#define ROM_BYTES (1 * 8192)
#define ROM_BASE  (0)
#define RAM_BASE  (0x2000)

namespace mem {

    void init();
    void deinit();

    extern uint8_t *mem_ram;
    extern uint8_t *mem_rom;

    // why? It makes things a _lot_ easier + compiler should be able to optimize it away
    inline uint8_t read_byte(uint32_t paddr) {
        if (paddr < (RAM_BASE + RAM_BYTES) && paddr >= RAM_BASE) {
            return mem_ram[paddr - RAM_BASE];
        }
        if (paddr < (ROM_BASE + ROM_BYTES) && paddr >= ROM_BASE) {
            return mem_rom[paddr - ROM_BASE];
        }
        return mmio::read(paddr);
    }

    inline void write_byte(uint32_t paddr, uint8_t value) {
        if (paddr < (RAM_BASE + RAM_BYTES) && paddr >= RAM_BASE) {
            mem_ram[paddr - RAM_BASE] = value;
        }
        mmio::write(paddr, value);
    }

    template <typename T> inline T read(uint64_t addr) {
        uint32_t val_u32 = 0;
        if (true) { // no MMU
            for (int i = 0; i < sizeof(T); i++) {
                val_u32 |= (uint64_t)read_byte(addr + i) << (i * 8);
            }
        }
        return (T)val_u32;
    }

    template <typename T> inline void write(uint64_t addr, T val) {
        uint64_t val_u64 = (uint64_t)val;
        if (true) { // no MMU
            for (int i = 0; i < sizeof(T); i++) {
                write_byte(addr + i, (val_u64 >> (i * 8)) & 0xFF);
            }
        }
    }
}
