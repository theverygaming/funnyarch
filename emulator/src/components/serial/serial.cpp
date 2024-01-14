#include <components/component.h>
#include <cstdio>
#include <fcntl.h>
#include <unistd.h>

static std::pair<uint32_t, bool> serial_read_callback(uint32_t addr) {
    if (addr == 0xF004B000) {
        char c;
        int n = read(STDIN_FILENO, &c, 1);
        if (n == 1) {
            return {(uint32_t)c | (1 << 9), true};
        }
        return {0, true};
    }
    return {0, false};
}

static bool serial_write_callback(uint32_t addr, uint32_t data) {
    if (addr == 0xF004B000) {
        fprintf(stderr, "%c", (char)(data & 0xFF));
        return true;
    }
    return false;
}

static void __attribute__((constructor)) init() {
    fcntl(STDIN_FILENO, F_SETFL, fcntl(STDIN_FILENO, F_GETFL) | O_NONBLOCK);

    component::add_mmio_read_callback(serial_read_callback);
    component::add_mmio_write_callback(serial_write_callback);
}
