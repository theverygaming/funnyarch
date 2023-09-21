#pragma once
#include <cstdint>

#include "mmio.h"

#define FB_LEN    ((640 * 480) / 8)
#define RAM_BYTES (((640 * 480) / 8) + 4096)
#define ROM_BYTES (1 * 8192)
#define ROM_BASE  (0)
#define RAM_BASE  (0x2000)

namespace mem {

    void init();
    void deinit();

    extern uint8_t *mem_ram;
    extern uint8_t *mem_rom;
    extern void *fb_base;

    template <typename T> inline T read(uint32_t addr) {
        if (addr < (RAM_BASE + (RAM_BYTES - 4)) && addr >= RAM_BASE) {
            return *(uint32_t *)&mem_ram[addr - RAM_BASE]; // TODO: endianness
        }
        if (addr < (ROM_BASE + (ROM_BYTES - 4)) && addr >= ROM_BASE) {
            return *((uint32_t *)&mem_rom[addr - ROM_BASE]); // TODO: endianness
        }
        return mmio::read(addr);
    }

    template <typename T> inline void write(uint32_t addr, T value) {
        if (addr < (RAM_BASE + (RAM_BYTES - 4)) && addr >= RAM_BASE) {
            *(uint32_t *)&mem_ram[addr - RAM_BASE] = value; // TODO: endianness
        }
        // TODO: maybe not defeat the purpose of "ROM"
        if (addr < (ROM_BASE + (ROM_BYTES - 4)) && addr >= ROM_BASE) {
            *(uint32_t *)&mem_rom[addr - ROM_BASE] = value; // TODO: endianness
        }
        mmio::write(addr, value);
    }
}
