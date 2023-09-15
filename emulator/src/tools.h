#pragma once

template <typename T> inline void bitset(T *c, uint8_t bit, bool value) {
    *c ^= (-value ^ *c) & (1 << bit);
}
