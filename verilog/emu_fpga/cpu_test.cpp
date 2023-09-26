#include "Vfpga_cpu_top.h"
#include "Vfpga_cpu_top___024root.h"
#include "sdl_class.h"
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <verilated.h>
#include <verilated_vcd_c.h>

#define GRAPHICS
// #define TRACE

int main(int argc, char **argv, char **env) {
    Vfpga_cpu_top *cpu = new Vfpga_cpu_top;
#ifdef GRAPHICS
    SDL sdl;
#endif
#ifdef TRACE
    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    cpu->trace(m_trace, 5);
    m_trace->open("waveform.vcd");
#endif

    cpu->clk_12m = 1;
    vluint64_t t;
    std::ifstream inf("output.bin", std::ios::binary);
    std::ofstream outf("output.txt");
    size_t memsize = (640 * 480) / 8;
    unsigned char *mem = new unsigned char[memsize];
    memset(mem, 0, memsize);
    for (size_t i = 0; i < memsize; i++) {
        inf.read((char *)&mem[i], sizeof(mem[i]));
        if (!inf.good()) {
            break;
        }
    }
    inf.close();

    char c = 0;

    auto start = std::chrono::high_resolution_clock::now();
    // for (t = 0; t < ((4) * (2 * 4)) + (4); t++) {
    // for (t = 0; t < 100; t++) {
    for (t = 0; true; t++) {
        cpu->clk_12m ^= 1;

        if (cpu->clk_12m == 1) {
            char cn = (cpu->dbg & 0b11111) | (1 << 6);
            if (cn != c) {
                fprintf(stderr, "OUT: %c\n", cn);
                c = cn;
            }
        }
        cpu->reset = t < 2 ? 1 : 0;

        cpu->eval();
#ifdef TRACE
        if (cpu->rootp->cpu__DOT__ctrl__DOT__state == 0 && cpu->clk_12m == 1) {
            if (cpu->rootp->cpu__DOT__ctrl__DOT__state == 0) {
                fprintf(stderr,
                        "r1: 0x%x r2: 0x%x r3: 0x%x r4: 0x%x rsp: 0x%x lr: 0x%x rf: 0x%x\n",
                        cpu->rootp->cpu__DOT__ctrl__DOT__regarr[01],
                        cpu->rootp->cpu__DOT__ctrl__DOT__regarr[02],
                        cpu->rootp->cpu__DOT__ctrl__DOT__regarr[03],
                        cpu->rootp->cpu__DOT__ctrl__DOT__regarr[04],
                        cpu->rootp->cpu__DOT__ctrl__DOT__regarr[29],
                        cpu->rootp->cpu__DOT__ctrl__DOT__regarr[28],
                        cpu->rootp->cpu__DOT__ctrl__DOT__regarr[31]);
            }
            fprintf(stderr, "\n");
        }
        m_trace->dump(t);
#endif
#ifdef GRAPHICS
        if (t % 400000 == 0) {
            sdl.redraw();
            if (!sdl.update_events()) {
                break;
            }
        }
#endif
    }
    auto end = std::chrono::high_resolution_clock::now();
    double ns = (double)std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
    double hz = (1 / ((ns / (t / 2)) / (1000000000)));
    fprintf(stderr, "simulation ran at %fMHz - %fns/clock cycle\n", hz / 1000000, ns / (t / 2));
    outf.close();
#ifdef TRACE
    m_trace->close();
#endif
    for (int i = 0; i < 32; i++) {
        fprintf(stderr, "r%d: 0x%x \n", i, cpu->rootp->fpga_cpu_top__DOT__cpu__DOT__ctrl__DOT__regarr[i]);
    }
#ifdef GRAPHICS
    sdl.full_redraw(mem, memsize);
    while (true) {
        if (!sdl.update_events()) {
            break;
        }
    }
#endif
    delete cpu;
    exit(EXIT_SUCCESS);
}
