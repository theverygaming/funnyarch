#include <chrono>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>

#include "cpu.h"
#include "sdl.h"

int main(int, char *[]) {
    cpu::init();

    sdl::init();
    fb::init();

    cpu::reset();

    std::ifstream input("output.bin", std::ios::binary);
    if (!input.good()) {
        fprintf(stderr, "failed to read output.bin\n");
        return 1;
    }
    input.read((char *)&cpu::cpuctx.mem_rom[0], ROM_BYTES);
    input.close();

    while (true) {
        sdl::loop();

        uint64_t instrs_executed = 0;
        auto t1 = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < 200; i++) {
            for (int i = 0; i < 1000000; i++) {
                // for (int i = 0; i < 100000; i++) {
                cpu::execute();
                instrs_executed++;
            }
            fb::redraw();
            sdl::loop();
        }
        auto t2 = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> exectime = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
        double mips = (1.0f / (exectime.count() / instrs_executed)) / 1000000;
        printf("%0.2f MIPS\n", mips);
        break;
    }

    /*uint64_t instrs_executed = 0;
    auto t1 = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < 20; i++) {
        cpu::execute();
        instrs_executed++;
    }
    auto t2 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> exectime = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
    double mips = (1.0f / (exectime.count() / instrs_executed)) / 1000000;
    printf("%0.2f MIPS\n", mips);*/

    for (int i = 0; i < 32; i++) {
        printf("%s: 0x%lx\n", cpudesc::regnames[i], cpu::cpuctx.regs[i]);
    }

    cpu::deinit();
    return 0;
}
