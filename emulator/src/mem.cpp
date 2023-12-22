#include "mem.h"
#include <cstring>

uint8_t *mem::mem_ram;
uint8_t *mem::mem_rom;
uint8_t *mem::mem_fb;

void mem::init() {
    mem_ram = new uint8_t[RAM_BYTES];
    mem_rom = new uint8_t[ROM_BYTES];
    mem_fb = new uint8_t[FB_BYTES];
    memset(mem_ram, 0, RAM_BYTES);
    memset(mem_rom, 0, ROM_BYTES);
    memset(mem_fb, 0, FB_BYTES);
}

void mem::deinit() {
    delete[] mem_ram;
    delete[] mem_rom;
    delete[] mem_fb;
}
