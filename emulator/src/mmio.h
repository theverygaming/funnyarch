#pragma once
#include <components/component.h>
#include <cstdint>
#include <cstdlib>

namespace mmio {
    inline uint32_t mread(uint32_t addr) {
        if (addr >= 0xF0000000) {
            return component::do_mmio_read(addr);
        }
        return rand();
    }

    inline void mwrite(uint32_t addr, uint32_t val) {
        if (addr >= 0xF0000000) {
            component::do_mmio_write(addr, val);
        }
    }
}
