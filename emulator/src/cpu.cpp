#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <utility>

#include "cpu.h"
#include "mem.h"

#define ARRLEN(x) (sizeof(x) / sizeof(x[0]))

cpu::cpu_except::cpu_except(etype e) {
    _e = e;
}

const char *cpu::cpu_except::what() const noexcept {
    return "CPU exception";
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
    cpuctx.regs[REG_IP] = RAM_BASE + 0x1000;
    cpuctx.regs[REG_SFLAGS] = (1 << 1); // supervisor mode
}

enum {
    OPC_NOP = 0x01,
    OPC_MOV = 0x02,
    OPC_ADD = 0x03,
    OPC_SUB = 0x04,
    OPC_DIV = 0x05,
    OPC_IDIV = 0x06,
    OPC_MUL = 0x07,
    OPC_IMUL = 0x08,
    OPC_REM = 0x09,
    OPC_IREM = 0x0A,
    OPC_SHR = 0x0B,
    OPC_SHL = 0x0C,
    OPC_SAR = 0x0D,
    OPC_AND = 0x0E,
    OPC_OR = 0x0F,
    OPC_XOR = 0x10,
    OPC_NOT = 0x11,
    OPC_TEST = 0x12,
    OPC_JMP = 0x13,
    OPC_RJMP = 0x14,
    OPC_CMP = 0x15,
    OPC_INT = 0x16,
    OPC_IRET = 0x17,
    OPC_WFI = 0x18,
    OPC_INVLPG = 0x19,
};

static const struct {
    const char *name;
    const unsigned int op_count;
} asm_opc_info[]{
    [0] = {"", 0},
    [OPC_NOP] = {"nop", 0},
    [OPC_MOV] = {"mov", 2},
    [OPC_ADD] = {"add", 2},
    [OPC_SUB] = {"sub", 2},
    [OPC_DIV] = {"div", 2},
    [OPC_IDIV] = {"idiv", 2},
    [OPC_MUL] = {"mul", 2},
    [OPC_IMUL] = {"imul", 2},
    [OPC_REM] = {"rem", 2},
    [OPC_IREM] = {"irem", 2},
    [OPC_SHR] = {"shr", 2},
    [OPC_SHL] = {"shl", 2},
    [OPC_SAR] = {"sar", 2},
    [OPC_AND] = {"and", 2},
    [OPC_OR] = {"or", 2},
    [OPC_XOR] = {"xor", 2},
    [OPC_NOT] = {"not", 2},
    [OPC_TEST] = {"test", 2},
    [OPC_JMP] = {"jmp", 1},
    [OPC_RJMP] = {"rjmp", 1},
    [OPC_CMP] = {"cmp", 2},
    [OPC_INT] = {"int", 1},
    [OPC_IRET] = {"iret", 0},
    [OPC_WFI] = {"wfi", 0},
    [OPC_INVLPG] = {"invlpg", 1},
};

static const unsigned int asm_op_sizes[]{
    [0] = 1,
    [1] = 2,
    [2] = 4,
    [3] = 8,
};

static void next_operand(uint64_t *ip, uint8_t opsize, uint8_t optype) {
    switch (optype) {
    case 0:
    case 1:
        (*ip)++;
        break;
    case 2:
        *ip += asm_op_sizes[opsize];
        break;
    case 3:
        *ip += 8;
        break;
    }
}

static uint64_t get_operand_val(uint64_t *ip, uint8_t opsize, uint8_t optype, bool derefreg = false, bool derefptr = false) {
    uint64_t val;

    if (optype <= 1) { // register
        val = mem::read_mem<uint8_t>(*ip);
    } else if (optype == 3) { // immediate pointer
        val = mem::read_mem<uint64_t>(*ip);
    } else { // immediate
        switch (opsize) {
        case 0:
            val = mem::read_mem<uint8_t>(*ip);
            break;
        case 1:
            val = mem::read_mem<uint16_t>(*ip);
            break;
        case 2:
            val = mem::read_mem<uint32_t>(*ip);
            break;
        case 3:
            val = mem::read_mem<uint64_t>(*ip);
            break;
        }
    }

    if (optype <= 1 && derefreg) { // register
        if (val >= ARRLEN(cpu::cpuctx.regs)) {
            throw cpu::cpu_except(cpu::cpu_except::etype::INVALIDOPCODE);
        }
        val = cpu::cpuctx.regs[val];
    }

    if ((optype == 3 || optype == 1) && derefptr) { // pointer
        switch (opsize) {
        case 0:
            val = mem::read_mem<uint8_t>(val);
            break;
        case 1:
            val = mem::read_mem<uint16_t>(val);
            break;
        case 2:
            val = mem::read_mem<uint32_t>(val);
            break;
        case 3:
            val = mem::read_mem<uint64_t>(val);
            break;
        }
    }

    uint64_t sizemask = (1ULL << (asm_op_sizes[opsize] * 8)) - 1;
    if ((asm_op_sizes[opsize] * 8) == 64) {
        sizemask = UINT64_MAX;
    }

    val &= sizemask;

    return val;
}

static void set_operand_val(uint64_t *ip, uint8_t opsize, uint8_t optype, uint64_t setval) {
    uint64_t val;

    if (optype <= 1) { // register
        val = mem::read_mem<uint8_t>(*ip);
    } else if (optype == 3) { // immediate pointer
        val = mem::read_mem<uint64_t>(*ip);
    } else { // immediate
        throw cpu::cpu_except(cpu::cpu_except::etype::INVALIDOPCODE);
    }

    if (optype <= 1) {
        if (val >= ARRLEN(cpu::cpuctx.regs)) {
            throw cpu::cpu_except(cpu::cpu_except::etype::INVALIDOPCODE);
        }
    }

    if (optype == 1) { // register pointer
        val = cpu::cpuctx.regs[val];
    }

    uint64_t sizemask = (1ULL << (asm_op_sizes[opsize] * 8)) - 1;
    if ((asm_op_sizes[opsize] * 8) == 64) {
        sizemask = UINT64_MAX;
    }

    if (optype == 0) { // register
        cpu::cpuctx.regs[val] = (cpu::cpuctx.regs[val] & ~sizemask) | (setval & sizemask);
    }

    if ((optype == 3 || optype == 1)) { // pointer
        switch (opsize) {
        case 0:
            mem::write_mem<uint8_t>(val, setval & sizemask);
            break;
        case 1:
            mem::write_mem<uint16_t>(val, setval & sizemask);
            break;
        case 2:
            mem::write_mem<uint32_t>(val, setval & sizemask);
            break;
        case 3:
            mem::write_mem<uint64_t>(val, setval & sizemask);
            break;
        }
    }
}

#define OPSIZE8  (0)
#define OPSIZE16 (1)
#define OPSIZE32 (2)
#define OPSIZE64 (3)

#define OPC(size, operation) ((uint16_t)operation | (size << 7))

/* clang-format off */
#define OPC_ALLSIZES(operation)    \
    OPC(OPSIZE8, operation):       \
    case OPC(OPSIZE16, operation): \
    case OPC(OPSIZE32, operation): \
    case OPC(OPSIZE64, operation)
/* clang-format on */

void cpu::execute() {
    uint64_t ip_mut = cpuctx.regs[REG_IP];

    uint16_t control = mem::read_mem<uint16_t>(cpuctx.regs[REG_IP]);
    uint8_t opcode = control & ((1UL << 7) - 1);
    uint8_t op_size = (control >> 7) & 0b11;
    uint8_t source_type = (control >> 9) & 0b11;
    uint8_t target_type = (control >> 11) & 0b11;
    uint8_t condition = (control >> 13) & 0b111;

    fprintf(stderr, "opc: 0x%x op_size: 0x%x source_type: 0x%x target_type: 0x%x condition: 0x%x\n", (unsigned int)opcode, (unsigned int)op_size, (unsigned int)source_type, (unsigned int)target_type, (unsigned int)condition);

    ip_mut += 2; // control

    if (opcode > OPC_INVLPG || opcode < 0x01) { // invalid opcode
        throw cpu_except(cpu_except::etype::INVALIDOPCODE);
    }

    if (asm_opc_info[opcode].op_count == 2 && target_type == 2) { // cannot have immediate as target
        throw cpu_except(cpu_except::etype::INVALIDOPCODE);
    }

    uint64_t sourceval = 0;
    if (asm_opc_info[opcode].op_count != 0) {
        sourceval = get_operand_val(&ip_mut, op_size, source_type, true, true);
        next_operand(&ip_mut, op_size, source_type);
    }
    fprintf(stderr, "    -> source value: 0x%llx\n", sourceval);

    fprintf(stderr, "    -> instr: %s\n", asm_opc_info[opcode].name);

    if (false) { // skip
        if (asm_opc_info[opcode].op_count == 2) {
            next_operand(&ip_mut, op_size, target_type);
        }
        cpuctx.regs[REG_IP] = ip_mut;
        return;
    }

    bool set_ip = true;

    switch (control & 0b111111111) {
    case OPC_ALLSIZES(OPC_NOP):
        break;

    case OPC_ALLSIZES(OPC_MOV): {
        set_operand_val(&ip_mut, op_size, target_type, sourceval);
        break;
    }
    case OPC_ALLSIZES(OPC_ADD):
        break;

    case OPC_ALLSIZES(OPC_SUB):
        break;

    case OPC_ALLSIZES(OPC_DIV):
        break;

    case OPC_ALLSIZES(OPC_IDIV):
        break;

    case OPC_ALLSIZES(OPC_MUL):
        break;

    case OPC_ALLSIZES(OPC_IMUL):
        break;

    case OPC_ALLSIZES(OPC_REM):
        break;

    case OPC_ALLSIZES(OPC_IREM):
        break;

    case OPC_ALLSIZES(OPC_SHR):
        break;

    case OPC_ALLSIZES(OPC_SHL):
        break;

    case OPC_ALLSIZES(OPC_SAR):
        break;

    case OPC_ALLSIZES(OPC_AND):
        break;

    case OPC_ALLSIZES(OPC_OR):
        break;

    case OPC_ALLSIZES(OPC_XOR):
        break;

    case OPC_ALLSIZES(OPC_NOT):
        break;

    case OPC_ALLSIZES(OPC_TEST):
        break;

    case OPC(OPSIZE64, OPC_JMP): {
        set_ip = false;
        cpuctx.regs[REG_IP] = sourceval;
        break;
    }

    case OPC(OPSIZE64, OPC_RJMP):
        break;

    case OPC_ALLSIZES(OPC_CMP):
        break;

    case OPC(OPSIZE8, OPC_INT):
        break;

    case OPC_ALLSIZES(OPC_IRET):
        break;

    case OPC_ALLSIZES(OPC_WFI):
        break;

    case OPC(OPSIZE64, OPC_INVLPG):
        break;

    default:
        throw cpu_except(cpu_except::etype::INVALIDOPCODE);
    }

    if (asm_opc_info[opcode].op_count == 2) {
        next_operand(&ip_mut, op_size, target_type);
    }

    /*uint64_t destop = 0;
    if (asm_opc_info[opcode].op_count == 2) {
        destop = get_operand_val(&ip_mut, op_size, target_type);
        next_operand(&ip_mut, op_size, target_type);
    }
    fprintf(stderr, "    -> dest value: 0x%llx\n", destop);*/

    if (set_ip) {
        cpuctx.regs[REG_IP] = ip_mut;
    }
}

const char *cpudesc::regnames[39] = {
    "r0",
    "r1",
    "r2",
    "r3",
    "r4",
    "r5",
    "r6",
    "r7",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "r13",
    "r14",
    "r15",
    "r16",
    "r17",
    "r18",
    "r19",
    "r20",
    "r21",
    "r22",
    "r23",
    "r24",
    "r25",
    "r26",
    "r27",
    "r28",
    "r29",
    "r30",
    "r31",
    "ip",
    "sp",
    "flags",
    "isp",
    "sflags",
    "ivt",
    "pd",
};
