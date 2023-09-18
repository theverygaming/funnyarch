#include <chrono>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>

#include "cpu.h"
#include "mem.h"
#include "sdl.h"

uint32_t mem_read(uint32_t addr) {
    return mem::read<uint32_t>(addr);
}

void mem_write(uint32_t addr, uint32_t data) {
    mem::write<uint32_t>(addr, data);
}

int main(int, char *[]) {
    mem::init();
    struct cpu::ctx cpu_ctx;
    cpu::init(&cpu_ctx);
    cpu_ctx.mem_read_ptr = &mem_read;
    cpu_ctx.mem_write_ptr = &mem_write;

    sdl::init();
    fb::init();

    std::ifstream input("output.bin", std::ios::binary);
    if (!input.good()) {
        fprintf(stderr, "failed to read output.bin\n");
        return 1;
    }
    input.read((char *)&mem::mem_rom[0], ROM_BYTES);
    input.close();

    while (true) {
        sdl::loop();

        uint64_t instrs_executed = 0;
        uint64_t clock_cycles = 0;
        auto t1 = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < 10; i++) {
            clock_cycles += cpu::execute(&cpu_ctx, 1000000);
            instrs_executed += 1000000;
            fb::redraw();
            sdl::loop();
        }
        auto t2 = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> exectime = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
        double mips = (1.0f / (exectime.count() / instrs_executed)) / 1000000;
        double freq = (1.0f / (exectime.count() / clock_cycles)) / 1000000;
        double usage =
            ((((double)clock_cycles) - ((double)instrs_executed * 2)) / (((double)instrs_executed * 3) - ((double)instrs_executed * 2))) * 100;
        printf("Average CPU usage: %0.2f%% - %0.2f MIPS - %0.2fMHz - %fs runtime\n", usage, mips, freq, exectime.count());
        break;
    }

    for (int i = 0; i < 32; i++) {
        printf("%s: 0x%x\n", cpudesc::regnames[i], cpu_ctx.regs[i]);
    }

    return 0;
}
