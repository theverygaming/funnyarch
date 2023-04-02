#pragma once
#include <stdio.h>
#include <stdlib.h>

#include "mmio.h"
#include "sdl.h"

namespace mmio {
    inline uint8_t read(uint64_t addr) {
        if (addr >= 1 && (addr - 1) < fb::buf_size) {
            return ((uint8_t *)fb::buf)[addr - 1];
        }
        return rand();
    }

    inline void write(uint64_t addr, uint8_t val) {
        if (addr == 0) {
            fprintf(stderr, "%c", (char)val);
        }
        if (addr >= 1 && (addr - 1) < fb::buf_size) {
            ((uint8_t *)fb::buf)[addr - 1] = val;
        }
    }
}
