#pragma once
#include <stdint.h>

inline void bitset(uint64_t *c, uint8_t bit, bool value) {
    *c ^= (-value ^ *c) & (1 << bit);
}
