#include "Vcpu.h"
#include "Vcpu___024root.h"
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdlib.h>
#include <verilated.h>
#include <verilated_vcd_c.h>

#define TRACE

int main(int argc, char **argv, char **env) {
    Vcpu *cpu = new Vcpu;

#ifdef TRACE
    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    cpu->trace(m_trace, 5);
    m_trace->open("waveform.vcd");
#endif

    cpu->clk = 1;
    auto start = std::chrono::high_resolution_clock::now();
    vluint64_t t;
    std::ifstream inf("output.bin", std::ios::binary);
    unsigned char *mem = new unsigned char[10000];
    memset(mem, 0, 10000);
    for (size_t i = 0; i < 10000; i++) {
        inf.read((char *)&mem[i], sizeof(mem[i]));
        if (!inf.good()) {
            break;
        }
    }
    inf.close();

    // for (t = 0; t < ((4) * (2 * 4)) + (4); t++) {
    for (t = 0; t < 5000; t++) {
        cpu->clk ^= 1;

        if (cpu->clk == 1) {
#ifdef TRACE
            printf("r1: 0x%x r2: 0x%x r3: 0x%x r4: 0x%x rsp: 0x%x lr: 0x%x\n",
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[1],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[2],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[3],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[4],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[29],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[28]);
#endif

            if (cpu->data_rw == 1) {
#ifdef TRACE
                printf("mem write A: 0x%x D: 0x%x\n", cpu->address, cpu->data);
#endif
                if (cpu->address >= 10000 - 4) {
                    break;
                }
                mem[cpu->address + 0] = (cpu->data >> 0) & 0xFF;
                mem[cpu->address + 1] = (cpu->data >> 8) & 0xFF;
                mem[cpu->address + 2] = (cpu->data >> 16) & 0xFF;
                mem[cpu->address + 3] = (cpu->data >> 24) & 0xFF;
            } else {
                if (cpu->address >= 10000 - 4) {
                    break;
                }
                vluint32_t data = ((uint32_t)mem[cpu->address + 0] << 0) | ((uint32_t)mem[cpu->address + 1] << 8) |
                                  ((uint32_t)mem[cpu->address + 2] << 16) | ((uint32_t)mem[cpu->address + 3] << 24);
                cpu->data = data;
#ifdef TRACE
                printf("mem read A: 0x%x D: 0x%x\n", cpu->address, cpu->data);
#endif
            }
        }
        cpu->reset = t < 2 ? 1 : 0;

        cpu->eval();
#ifdef TRACE
        printf("\n");
        m_trace->dump(t);
#endif
    }
    auto end = std::chrono::high_resolution_clock::now();
    double hz = (1 / (((double)std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count() / t) / (1000000000)));
    printf("simulation ran at %fMHz", hz / 1000000);
#ifdef TRACE
    m_trace->close();
#endif
    delete cpu;
    exit(EXIT_SUCCESS);
}
