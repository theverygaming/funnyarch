#include <cassert>
#include <chrono>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>

#include "cpu.h"
#include "mem.h"
#include "sdl_class.h"

#define GRAPHICS

#ifdef GRAPHICS
static SDL sdl_ctx;
#endif

uint32_t mem_read(uint32_t addr) {
    return mem::read<uint32_t>(addr);
}

void mem_write(uint32_t addr, uint32_t data) {
    mem::write<uint32_t>(addr, data);
#ifdef GRAPHICS
    sdl_ctx.mem_write(addr, data);
#endif
}

int main(int, char *[]) {
    mem::init();
    sdl_ctx.set_buf(mem::fb_base, FB_LEN);
    struct cpu::ctx cpu_ctx;
    cpu::init(&cpu_ctx);
    cpu_ctx.mem_read_ptr = &mem_read;
    cpu_ctx.mem_write_ptr = &mem_write;

    std::ifstream input("output.bin", std::ios::binary);
    if (!input.good()) {
        fprintf(stderr, "failed to read output.bin\n");
        return 1;
    }
    input.read((char *)&mem::mem_rom[0], ROM_BYTES);
    input.close();
    bool running = true;
    while (running) {
        uint64_t instr_count = 1000000;
        uint64_t repeat_count = 1000;
        uint64_t instrs_executed = instr_count * repeat_count;
        uint64_t clock_cycles = 0;
        auto t1 = std::chrono::high_resolution_clock::now();
        for (uint64_t i = 0; i < repeat_count; i++) {
#ifdef GRAPHICS
            if (!sdl_ctx.update_events()) {
                running = false;
                break;
            }
            sdl_ctx.redraw();
#endif
            uint64_t cycles_executed = cpu::execute(&cpu_ctx, instr_count);
            clock_cycles += cycles_executed;
        }
        auto t2 = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> exectime = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
        double mips = (1.0f / (exectime.count() / instrs_executed)) / 1000000;
        double freq = (1.0f / (exectime.count() / clock_cycles)) / 1000000;
        double cycles_min = ((double)instrs_executed * 2);
        double cycles_max = ((double)instrs_executed * 3);
        assert(clock_cycles >= cycles_min);
        double usage = (((double)clock_cycles - cycles_min) / (cycles_max - cycles_min)) * 100;
        printf("\nAverage CPU usage: %0.2f%% - %0.2f MIPS - %0.2fMHz - %fs runtime\n", usage, mips, freq, exectime.count());
        // break;
    }

    for (int i = 0; i < 32; i++) {
        printf("%s: 0x%x\n", cpudesc::regnames[i], cpu_ctx.regs[i]);
    }

    return 0;
}
