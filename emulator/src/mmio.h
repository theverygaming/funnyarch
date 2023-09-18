#pragma once
#include <stdio.h>
#include <stdlib.h>

#include "mmio.h"
#include "sdl.h"

namespace mmio {
    inline uint32_t read(uint32_t addr) {
        if (addr >= 1 && (addr - 1) < fb::buf_size) {
            // return ((uint8_t *)fb::buf)[addr - 1]; // TODO: endianness
        }
        if (addr == 0xFFFFFFFC) {
            return 0x02; // JMP(E4) #0
        }
        return rand();
    }

    inline void write(uint32_t addr, uint32_t val) {
        if (addr == 0x1000) {
            fprintf(stderr, "%c", (char)(val & 0xFF));
        }
        if (addr >= 1 && (addr - 1) < fb::buf_size) {
            // ((uint8_t *)fb::buf)[addr - 1] = val; // TODO: endianness
        }
    }
}
