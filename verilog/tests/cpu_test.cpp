#include "Vcpu.h"
#include "Vcpu___024root.h"
#include <chrono>
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
    // for (t = 0; t < ((4) * (2 * 4)) + (4); t++) {
    for (t = 0; t < 5000; t++) {
        cpu->clk ^= 1;

        if (cpu->clk == 1) {
#ifdef TRACE
            printf("r1: %d r2: %d r3: %d r4: %d\n",
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[1],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[2],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[3],
                   cpu->rootp->cpu__DOT__ctrl__DOT__regarr[4]);
#endif

            if (cpu->data_rw == 1) {
#ifdef TRACE
                printf("mem write A: 0x%x D: 0x%x\n", cpu->address, cpu->data);
#endif
            } else {
                vluint32_t data;
                inf.seekg(cpu->address);
                inf.read((char *)&data, sizeof(data));
                if (!inf.good()) {
                    break;
                }
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