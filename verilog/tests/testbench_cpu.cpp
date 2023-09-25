#include "Vcpu.h"
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <verilated.h>
#include <verilated_vcd_c.h>

// #define TRACE

int main(int argc, char **argv, char **env) {
    int exitcode = EXIT_SUCCESS;
    Vcpu *cpu = new Vcpu;
#ifdef TRACE
    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    cpu->trace(m_trace, 5);
    m_trace->open("out/testbench_cpu_waveform.vcd");
#endif
    cpu->clk = 0;
    for (vluint64_t t = 0; t < 200000; t++) {
        cpu->clk = cpu->clk ^ 1;

        cpu->eval();
#ifdef TRACE
        m_trace->dump(t);
#endif
    }
exit:
#ifdef TRACE
    m_trace->close();
#endif
#ifdef COVERAGE
    Verilated::threadContextp()->coveragep()->write("out/testbench_cpu_coverage.dat");
#endif
    delete cpu;
    exit(exitcode);
}
