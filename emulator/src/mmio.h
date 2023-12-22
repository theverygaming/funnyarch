#pragma once
#include <stdio.h>
#include <stdlib.h>

namespace mmio {

    inline uint32_t read(uint32_t addr) {
        if (addr == 0xF004B000) {
            char c;
            int n = fread(&c, 1, 1, stdin);
            if (n == 1) {
                return (uint32_t)c | (1 << 9);
            }
            return 0;
        }
        return rand();
    }

    inline void write(uint32_t addr, uint32_t val) {
        if (addr == 0xF004B000) {
            fprintf(stderr, "%c", (char)(val & 0xFF));
        }
    }
}
