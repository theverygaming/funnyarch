#include <components/component.h>
#include <cstdio>
#include <cstring>

static struct hdd {
    FILE *file;
    unsigned int command; // 0 = none, 1 = read, 2 = write
    bool finished;
    uint32_t sector_idx;

    uint32_t numsectors;
} hdd_state;

static uint8_t *databuf;

static inline bool is_running_cmd() {
    return (hdd_state.command == 0) ? false : (!hdd_state.finished);
}

static inline void run_cmd() {
    if ((hdd_state.file != NULL) && (hdd_state.command != 0)) {
        fseek(hdd_state.file, hdd_state.sector_idx * 512, SEEK_SET);
        memset(databuf, 0, 512);
        size_t nbytes;
        switch (hdd_state.command) {
        case 1:
            nbytes = fread(databuf, 1, 512, hdd_state.file);
            break;
        case 2:
            nbytes = fwrite(databuf, 1, 512, hdd_state.file);
            break;
        }
        hdd_state.finished = true;
    }
}

static std::pair<uint32_t, bool> hdd_read_callback(uint32_t addr) {
    if (addr == 0xF004B004) { // HDD control/status register
        uint32_t n = (hdd_state.command & 0b11) | (hdd_state.finished ? 0b100 : 0) | ((hdd_state.sector_idx & 0x1FFFFFFF) << 3);
        return {n, true};
    }
    if (addr == 0xF004B008) { // HDD info register
        uint32_t n = hdd_state.numsectors & 0x1FFFFFFF;
        return {n, true};
    }
    if (addr == 0xF004B00C) { // HDD controller control/status register
        return {0, true};
    }
    if ((addr >= 0xF004B010) && (addr < 0xF004B210)) { // HDD data buffer
        uint32_t offset = addr - 0xF004B010;
        offset -= offset % 4; // align
        return {databuf[offset] | (databuf[offset + 1] << 8) | (databuf[offset + 2] << 16) | (databuf[offset + 3] << 24), true};
    }
    return {0, false};
}

static bool hdd_write_callback(uint32_t addr, uint32_t data) {
    if (addr == 0xF004B004) { // HDD control/status register
        unsigned int new_cmd = data & 0b11;
        if (new_cmd > 3) {
            new_cmd = 0;
        }
        uint32_t new_sector_idx = (data >> 3) & 0x1FFFFFFF;
        hdd_state.command = new_cmd;
        hdd_state.finished = false;
        hdd_state.sector_idx = new_sector_idx;
        run_cmd();
        return true;
    }
    if (addr == 0xF004B008) { // HDD info register
        return true;
    }
    if (addr == 0xF004B00C) { // HDD controller control/status register
        return true;
    }
    if ((addr >= 0xF004B010) && (addr < 0xF004B210)) { // HDD data buffer
        uint32_t offset = addr - 0xF004B010;
        offset -= offset % 4; // align
        if (!is_running_cmd()) {
            databuf[offset] = data & 0xFF;
            databuf[offset + 1] = (data >> 8) & 0xFF;
            databuf[offset + 2] = (data >> 16) & 0xFF;
            databuf[offset + 3] = (data >> 24) & 0xFF;
        }
        return true;
    }
    return false;
}

static void __attribute__((constructor)) init() {
    hdd_state.file = fopen("hd.bin", "r+");
    hdd_state.command = 0;
    hdd_state.finished = 0;
    hdd_state.sector_idx = 0;
    hdd_state.numsectors = 0;

    if (hdd_state.file != NULL) {
        fseek(hdd_state.file, 0, SEEK_END);
        hdd_state.numsectors = ftell(hdd_state.file) / 512;
    }

    databuf = new uint8_t[512];
    memset(databuf, 0, 512);
    component::add_mmio_read_callback(hdd_read_callback);
    component::add_mmio_write_callback(hdd_write_callback);
}
