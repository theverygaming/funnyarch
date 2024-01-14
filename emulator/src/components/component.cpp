#include <components/component.h>
#include <cstdlib>
#include <vector>

std::vector<std::pair<uint32_t, bool> (*)(uint32_t)> read_callbacks;
std::vector<bool (*)(uint32_t, uint32_t)> write_callbacks;

void component::add_mmio_read_callback(std::pair<uint32_t, bool> (*callback)(uint32_t addr)) {
    read_callbacks.push_back(callback);
}

void component::add_mmio_write_callback(bool (*callback)(uint32_t addr, uint32_t data)) {
    write_callbacks.push_back(callback);
}

uint32_t component::do_mmio_read(uint32_t addr) {
    for (auto &callback : read_callbacks) {
        auto [data, success] = callback(addr);
        if (success) {
            return data;
        }
    }
    return rand();
}

void component::do_mmio_write(uint32_t addr, uint32_t data) {
    for (auto &callback : write_callbacks) {
        bool success = callback(addr, data);
        if (success) {
            break;
        }
    }
}
