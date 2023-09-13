#include "Vcpu.h"
#include "Vcpu___024root.h"
#include "sdl_class.h"
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdlib.h>
#include <verilated.h>
#include <verilated_vcd_c.h>

#define GRAPHICS
// #define TRACE

int main(int argc, char **argv, char **env) {
    Vcpu *cpu = new Vcpu;
#ifdef GRAPHICS
    SDL sdl;
#endif
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

    // for (t = 0; t < ((4) * (2 * 4)) + (4); t++) {
    // for (t = 0; t < 100; t++) {
    for (t = 0; true; t++) {
        cpu->clk ^= 1;

        if (cpu->clk == 1) {
#ifdef TRACE
            if ((cpu->address & 0b11) != 0) {
                fprintf(stderr, "unaligned access @0x%x\n", cpu->address);
            }
#endif

            if (cpu->data_rw == 1) {
#ifdef TRACE
                fprintf(stderr, "mem write A: 0x%x D: 0x%x\n", cpu->address, cpu->data);
#endif
                if (cpu->address >= memsize - 4) {
                    break;
                }
                *(uint32_t *)&mem[cpu->address] = cpu->data; // TODO: endianness
                if (cpu->address == 0x1000) {
                    outf.write((const char *)&mem[cpu->address], 1);
                    printf("%c", mem[cpu->address]);
                    fprintf(stderr, "OUTPUT CHAR: %c\n", mem[cpu->address]);
                }
            } else {
                if (cpu->address >= memsize - 4) {
                    break;
                }
                cpu->data = *(uint32_t *)&mem[cpu->address]; // TODO: endianness
#ifdef TRACE
                fprintf(stderr, "mem read A: 0x%x D: 0x%x\n", cpu->address, cpu->data);
#endif
            }
        }
        cpu->reset = t < 2 ? 1 : 0;

        cpu->eval();
#ifdef TRACE
        if (cpu->rootp->cpu__DOT__ctrl__DOT__state == 0 && cpu->clk == 1) {
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
            sdl.redraw(mem, memsize);
            if (!sdl.update()) {
                break;
            }
        }
#endif
    }
    auto end = std::chrono::high_resolution_clock::now();
    double hz = (1 / (((double)std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count() / t) / (1000000000)));
    fprintf(stderr, "simulation ran at %fMHz", hz / 1000000);
    outf.close();
#ifdef TRACE
    m_trace->close();
#endif
    fprintf(stderr, "r10: 0x%x \n", cpu->rootp->cpu__DOT__ctrl__DOT__regarr[10]);
#ifdef GRAPHICS
    while (true) {
        if (!sdl.update()) {
            break;
        }
    }
#endif
    delete cpu;
    exit(EXIT_SUCCESS);
}
