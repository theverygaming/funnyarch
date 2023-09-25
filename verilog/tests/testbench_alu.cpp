#include "Valu.h"
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <verilated.h>
#include <verilated_vcd_c.h>

// #define TRACE

int main(int argc, char **argv, char **env) {
    int exitcode = EXIT_SUCCESS;
    Valu *alu = new Valu;
#ifdef TRACE
    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    alu->trace(m_trace, 5);
    m_trace->open("out/testbench_alu_waveform.vcd");
#endif
    srand(0);

    for (vluint64_t t = 0; t < 200000; t++) {
        vluint64_t tmp;
        vluint32_t in_opcode, in_1, in_2;
        vluint32_t expect_out, expect_carry, expect_zero;

        in_1 = rand() * rand();
        in_2 = rand() * rand() * t;

        in_opcode = (t % 10) + 1;
        switch (in_opcode) {
        case 1:
            expect_carry = __builtin_add_overflow(in_1, in_2, &expect_out);
            break;
        case 2:
            expect_carry = __builtin_sub_overflow(in_1, in_2, &expect_out);
            break;
        case 3:
            tmp = (vluint64_t)in_1 << (in_2 & 0b11111);
            expect_out = tmp;
            expect_carry = (tmp >> 32) & 0x1;
            break;
        case 4:
            expect_out = in_1 >> (in_2 & 0b11111);
            expect_carry = 0;
            break;
        case 5:
            expect_out = (int32_t)in_1 >> (in_2 & 0b11111);
            expect_carry = 0;
            break;
        case 6:
            expect_out = in_1 & in_2;
            expect_carry = 0;
            break;
        case 7:
            expect_out = in_1 | in_2;
            expect_carry = 0;
            break;
        case 8:
            expect_out = in_1 ^ in_2;
            expect_carry = 0;
            break;
        case 9:
            expect_out = ~in_1;
            expect_carry = 1;
            break;
        default:
            expect_out = 0;
            expect_carry = 0;
            break;
        }

        expect_zero = expect_out == 0;
        alu->opcode = in_opcode;
        alu->in1 = in_1;
        alu->in2 = in_2;

        alu->eval();
#ifdef TRACE
        m_trace->dump(t);
#endif

        if ((expect_out != alu->out) || (expect_carry != alu->carry) || (expect_zero != alu->zero)) {
            fprintf(stderr, "ALU opcode 0x%x failed\n", in_opcode);
            fprintf(stderr, "in1: 0x%x in2: 0x%x\ngot:      out: 0x%x carry: 0x%x zero: 0x%x\n", in_1, in_2, alu->out, alu->carry, alu->zero);
            fprintf(stderr, "expected: out: 0x%x carry: 0x%x zero: 0x%x\n", expect_out, expect_carry, expect_zero);
            exitcode = 1;
            goto exit;
        }
    }
exit:
#ifdef TRACE
    m_trace->close();
#endif
#ifdef COVERAGE
    Verilated::threadContextp()->coveragep()->write("out/testbench_alu_coverage.dat");
#endif
    delete alu;
    exit(exitcode);
}
