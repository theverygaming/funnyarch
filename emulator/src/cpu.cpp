#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include <utility>

#include "cpu.h"
#include "mem.h"
#include "tools.h"

// #define ISDEBUG

#ifdef ISDEBUG
#define DEBUG_PRINTF(...) fprintf(stderr, __VA_ARGS__)
#else
#define DEBUG_PRINTF(...) \
    do {                  \
    } while (0)
#endif

static inline long signexpand(unsigned long value, unsigned int bits) {
    if ((value >> (bits - 1)) != 0) {
        value |= ~((1ul << bits) - 1);
    }
    return value;
}

cpu::cpu_except::cpu_except(etype e) {
    _e = e;
}

const char *cpu::cpu_except::what() const noexcept {
    switch (_e) {
    case etype::PAGEFAULT:
        return "CPU exception - page fault";
    case etype::PROTECTIONFAULT:
        return "CPU exception - protection fault";
    case etype::INVALIDOPCODE:
        return "CPU exception - invalid opcode";
    case etype::DIVIDEBYZERO:
        return "CPU exception - divide by zero";
    }
    return "unknown CPU exception";
}

struct cpu::cpu cpu::cpuctx;

void cpu::init() {
    cpuctx.mem_ram = new uint8_t[RAM_BYTES];
    cpuctx.mem_rom = new uint8_t[ROM_BYTES];
}

void cpu::deinit() {
    delete[] cpuctx.mem_ram;
    delete[] cpuctx.mem_rom;
}

void cpu::reset() {
    int fd = open("/dev/random", O_RDONLY);
    read(fd, cpuctx.mem_ram, sizeof(RAM_BYTES));
    close(fd);
    memset(cpuctx.regs, 0, sizeof(cpuctx.regs));
    cpuctx.regs[REG_IP] = ROM_BASE;
}

static bool shouldexecute(uint8_t condition) {
    switch (condition) {
    case 0: // always
        return true;
    case 1: // if equal
        return (cpu::cpuctx.regs[REG_FLAGS] & 0b10) != 0;
    case 2: // if not equal
        return (cpu::cpuctx.regs[REG_FLAGS] & 0b10) == 0;
    case 3: // if less than
        return (cpu::cpuctx.regs[REG_FLAGS] & 0b01) != 0;
    case 4: // if greater than or equal
        return (cpu::cpuctx.regs[REG_FLAGS] & 0b01) == 0;
    case 5: // if greater than
        return (cpu::cpuctx.regs[REG_FLAGS] & 0b11) == 0;
    case 6: // if less than or equal
        return (cpu::cpuctx.regs[REG_FLAGS] & 0b11) != 0;
    }
    return true;
}

struct __attribute__((packed)) enc_1 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int src1 : 5;
    unsigned int src2 : 5;
    unsigned int tgt : 5;
    unsigned int instr_spe : 8;
};

struct __attribute__((packed)) enc_2 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int src : 5;
    unsigned int tgt : 5;
    unsigned int imm13 : 13;
};

struct __attribute__((packed)) enc_3 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int tgt : 5;
    unsigned int instr_spe : 2;
    unsigned int imm16 : 16;
};

struct __attribute__((packed)) enc_4 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned long imm23 : 23;
};

struct __attribute__((packed)) enc_5 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int tgt : 5;
    unsigned long instr_spe : 18;
};

struct __attribute__((packed)) enc_6 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned long instr_spe : 23;
};

struct __attribute__((packed)) enc_7 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int src : 5;
    unsigned int tgt : 5;
    unsigned int instr_spe : 13;
};

void cpu::execute() {
    uint32_t instr = mem::read<uint32_t>(cpuctx.regs[REG_IP] & 0xFFFFFFFC);
    cpuctx.regs[REG_IP] += 4;
    uint8_t opcode = instr & 0x3F;
    uint8_t cond = (instr >> 6) & 0x07;

    if (!shouldexecute(cond)) {
        DEBUG_PRINTF("SKIPPING ");
        DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (cpuctx.regs[REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);
        return;
    }

    DEBUG_PRINTF("ip: 0x%x istr: 0x%x opc: 0x%x\n", (cpuctx.regs[REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);

    switch (opcode) {
    case 0x00: { /* NOP(E6) */
        break;
    }

    case 0x01: { /* STRPI(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        cpuctx.regs[e.tgt] += signexpand(e.imm13, 13);
        mem::write<uint32_t>(cpuctx.regs[e.tgt], cpuctx.regs[e.src]);
        break;
    }

    case 0x02: { /* JMP(E4) */
        struct enc_4 e = *((struct enc_4 *)&instr);
        cpuctx.regs[REG_IP] = e.imm23 * 4;
        break;
    }

    case 0x03: { /* RJMP(E4) */
        struct enc_4 e = *((struct enc_4 *)&instr);
        cpuctx.regs[REG_IP] += signexpand(e.imm23, 23) * 4;
        break;
    }

    case 0x04: { /* MOV(E7) */
        struct enc_7 e = *((struct enc_7 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src];
        break;
    }

    case 0x05: { /* MOV(E3) */
        struct enc_3 e = *((struct enc_3 *)&instr);
        if (e.instr_spe == 0b01) {
            cpuctx.regs[e.tgt] = (cpuctx.regs[e.tgt] & 0xFFFF) | (e.imm16 << 16);
        } else {
            cpuctx.regs[e.tgt] = e.imm16;
        }
        break;
    }

    case 0x07: { /* LDRI(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        cpuctx.regs[e.tgt] = mem::read<uint32_t>(cpuctx.regs[e.src]);
        cpuctx.regs[e.src] += signexpand(e.imm13, 13);
        break;
    }

    case 0x08: { /* STR(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        mem::write<uint32_t>(cpuctx.regs[e.tgt] + signexpand(e.imm13, 13), cpuctx.regs[e.src]);
        break;
    }

    case 0x0a: { /* JAL(E4) */
        struct enc_4 e = *((struct enc_4 *)&instr);
        cpuctx.regs[REG_LR] = cpuctx.regs[REG_IP];
        cpuctx.regs[REG_IP] = e.imm23 * 4;
        break;
    }

    case 0x0b: { /* RJAL(E4) */
        struct enc_4 e = *((struct enc_4 *)&instr);
        cpuctx.regs[REG_LR] = cpuctx.regs[REG_IP];
        cpuctx.regs[REG_IP] += signexpand(e.imm23, 23) * 4;
        break;
    }

    case 0x0c: { /* CMP(E7) */
        struct enc_7 e = *((struct enc_7 *)&instr);
        uint32_t result;
        bool carry = __builtin_sub_overflow(cpuctx.regs[e.tgt], cpuctx.regs[e.src], &result);
        bitset(&cpuctx.regs[REG_FLAGS], 0, carry);
        bitset(&cpuctx.regs[REG_FLAGS], 1, result == 0);
        break;
    }

    case 0x0d: { /* CMP(E3) */
        struct enc_3 e = *((struct enc_3 *)&instr);
        uint32_t result;
        bool carry = __builtin_sub_overflow(cpuctx.regs[e.tgt], e.imm16, &result);
        bitset(&cpuctx.regs[REG_FLAGS], 0, carry);
        bitset(&cpuctx.regs[REG_FLAGS], 1, result == 0);
        break;
    }

    case 0x10: { /* ADD(E1) */
        struct enc_1 e = *((struct enc_1 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src1] + cpuctx.regs[e.src2];
        break;
    }

    case 0x11: { /* ADD(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src] + e.imm13;
        break;
    }

    case 0x12: { /* ADD(E3) */
        struct enc_3 e = *((struct enc_3 *)&instr);
        if (e.instr_spe == 0b01) {
            cpuctx.regs[e.tgt] += e.imm16 << 16;
        } else {
            cpuctx.regs[e.tgt] += e.imm16;
        }
        break;
    }

    case 0x13: { /* SUB(E1) */
        struct enc_1 e = *((struct enc_1 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src1] - cpuctx.regs[e.src2];
        break;
    }

    case 0x14: { /* SUB(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src] - e.imm13;
        break;
    }

    case 0x15: { /* SUB(E3) */
        struct enc_3 e = *((struct enc_3 *)&instr);
        if (e.instr_spe == 0b01) {
            cpuctx.regs[e.tgt] -= e.imm16 << 16;
        } else {
            cpuctx.regs[e.tgt] -= e.imm16;
        }
        break;
    }

    case 0x16: { /* SHL(E1) */
        struct enc_1 e = *((struct enc_1 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src2] <= 31 ? (cpuctx.regs[e.src1] << cpuctx.regs[e.src2]) : 0;
        break;
    }

    case 0x17: { /* SHL(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        cpuctx.regs[e.tgt] = e.imm13 <= 31 ? (cpuctx.regs[e.src] << e.imm13) : 0;
        break;
    }

    case 0x18: { /* SHR(E1) */
        struct enc_1 e = *((struct enc_1 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src2] <= 31 ? (cpuctx.regs[e.src1] >> cpuctx.regs[e.src2]) : 0;
        break;
    }

    case 0x19: { /* SHR(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        cpuctx.regs[e.tgt] = e.imm13 <= 31 ? (cpuctx.regs[e.src] >> e.imm13) : 0;
        break;
    }

    case 0x1A: { /* SAR(E1) */
        struct enc_1 e = *((struct enc_1 *)&instr);
        cpuctx.regs[e.tgt] = cpuctx.regs[e.src2] <= 31 ? ((int32_t)cpuctx.regs[e.src1] >> cpuctx.regs[e.src2]) : 0;
        break;
    }

    case 0x1B: { /* SAR(E2) */
        struct enc_2 e = *((struct enc_2 *)&instr);
        cpuctx.regs[e.tgt] = e.imm13 <= 31 ? ((int32_t)cpuctx.regs[e.src] >> e.imm13) : 0;
        break;
    }

    default:
        fprintf(stderr, "ip: 0x%x istr: 0x%x opc: 0x%x\n", (cpuctx.regs[REG_IP] - 4) & 0xFFFFFFFC, instr, opcode);
        throw cpu_except(cpu_except::etype::INVALIDOPCODE);
    }

    /*for (int i = 0; i < 32; i++) {
        printf("%s: 0x%lx | ", cpudesc::regnames[i], cpuctx.regs[i]);
    }
    printf("\n");*/
}

const char *cpudesc::regnames[32] = {
    "r0",  "r1",  "r2",  "r3",  "r4",  "r5",  "r6",  "r7",  "r8",  "r9",  "r10", "r11", "r12", "r13", "r14", "r15",
    "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23", "r24", "r25", "r26", "r27", "lr",  "rsp", "rip", "rf",
};
