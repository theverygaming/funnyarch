#include "Vfpga_cpu_top.h"
#include "Vfpga_cpu_top___024root.h"
#include "sdl_class.h"
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
    Vfpga_cpu_top *cpu = new Vfpga_cpu_top;
#ifdef TRACE
    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    cpu->trace(m_trace, 5);
    m_trace->open("waveform.vcd");
#endif

    cpu->clk_12m = 1;
    vluint64_t t;
    std::ifstream inf("output.bin", std::ios::binary);

    auto start = std::chrono::high_resolution_clock::now();
    char c = '0';
    for (t = 0; t < 12000000 * 10; t++) {
        // for (t = 0; true; t++) {
        cpu->clk_12m ^= 1;

        if (cpu->clk_12m == 1) {
            /*if (cpu->rootp->fpga_cpu_top__DOT__address == 0x1000 && ((t % 4) == 1)) {
                printf("%c", cpu->rootp->fpga_cpu_top__DOT__data);
                fprintf(stderr, "OUTPUT CHAR: %c\n", cpu->rootp->fpga_cpu_top__DOT__data);
            }*/
        }
        char cn = (cpu->dbg & 0b11111) | (1 << 6);
        if(cn != c)  {
            fprintf(stderr, "%c", cn);
            c = cn;
        }


        cpu->reset = t < 2 ? 1 : 0;

        cpu->eval();
#ifdef TRACE
        m_trace->dump(t);
#endif
    }

    auto end = std::chrono::high_resolution_clock::now();
    double ns = (double)std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
    double hz = (1 / ((ns / (t / 2)) / (1000000000)));
    fprintf(stderr, "simulation ran at %fMHz - %fns/clock cycle\n", hz / 1000000, ns / (t / 2));
#ifdef TRACE
    m_trace->close();
#endif
    for (int i = 0; i < 32; i++) {
        // fprintf(stderr, "r%d: 0x%x \n", i, cpu->rootp->cpu__DOT__ctrl__DOT__regarr[i]);
    }
    delete cpu;
    exit(EXIT_SUCCESS);
}
