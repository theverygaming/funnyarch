#include "mem.h"

uint8_t *mem::mem_ram;
uint8_t *mem::mem_rom;

void mem::init() {
    mem_ram = new uint8_t[RAM_BYTES];
    mem_rom = new uint8_t[ROM_BYTES];
}

void mem::deinit() {
    delete[] mem_ram;
    delete[] mem_rom;
}
