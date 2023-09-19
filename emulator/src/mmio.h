#pragma once
#include <stdio.h>
#include <stdlib.h>

namespace mmio {
    inline uint32_t read(uint32_t addr) {
        if (addr == 0xFFFFFFFC) {
            return 0x02; // JMP(E4) #0
        }
        return rand();
    }

    inline void write(uint32_t addr, uint32_t val) {
        if (addr == 0x1000) {
            fprintf(stderr, "%c", (char)(val & 0xFF));
        }
    }
}
