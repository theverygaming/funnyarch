#include "mem.h"
#include <cstring>

uint8_t *mem::mem_ram;
uint8_t *mem::mem_rom;
void *mem::fb_base;

void mem::init() {
    mem_ram = new uint8_t[RAM_BYTES];
    mem_rom = new uint8_t[ROM_BYTES];
    memset(mem_ram, 0, RAM_BYTES);
    memset(mem_rom, 0, ROM_BYTES);
    fb_base = &mem_ram[RAM_BYTES - FB_LEN];
}

void mem::deinit() {
    delete[] mem_ram;
    delete[] mem_rom;
}
