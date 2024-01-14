#pragma once
#include <cstdint>
#include <utility>

namespace component {
    void add_mmio_read_callback(std::pair<uint32_t, bool> (*callback)(uint32_t addr));
    void add_mmio_write_callback(bool (*callback)(uint32_t addr, uint32_t data));

    uint32_t do_mmio_read(uint32_t addr);
    void do_mmio_write(uint32_t addr, uint32_t data);
}
