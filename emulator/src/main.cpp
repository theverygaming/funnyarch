#include <fstream>
#include <stdio.h>
#include <stdlib.h>

#include "cpu.h"

int main(int, char *[]) {
    std::ifstream inf("out.bin", std::ios::binary);
    cpu::init();

    std::ifstream input("out.bin", std::ios::binary);

    input.seekg(0, input.end);
    size_t fsize = input.tellg();
    input.seekg(0, input.beg);

    input.read((char *)&cpu::cpuctx.mem_ram[0x1000], fsize);

    input.close();

    cpu::reset();

    for (int i = 0; i < 20; i++) {
        cpu::execute();
    }

    for (int i = 0; i < 39; i++) {
        printf("%s: 0x%lx\n", cpudesc::regnames[i], cpu::cpuctx.regs[i]);
    }

    cpu::deinit();
    return 0;
}
