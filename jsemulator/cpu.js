"use strict";

class funnyarchCPUInstrEncoding1 {
    constructor(instr) {
        this.instr = instr >>> 0;
        this.str = {};
        this.str.opcode = (instr & 0x3F) >>> 0;
        this.str.condition = ((instr >>> 6) & 0x07) >>> 0;
        this.str.src1 = ((instr >>> 9) & 0x1F) >>> 0;
        this.str.src2 = ((instr >>> 14) & 0x1F) >>> 0;
        this.str.tgt = ((instr >>> 19) & 0x1F) >>> 0;
        this.str.instr_spe = ((instr >>> 24) & 0xFF) >>> 0;
    }
}

class funnyarchCPUInstrEncoding2 {
    constructor(instr) {
        this.instr = instr >>> 0;
        this.str = {};
        this.str.opcode = (instr & 0x3F) >>> 0;
        this.str.condition = ((instr >>> 6) & 0x07) >>> 0;
        this.str.src = ((instr >>> 9) & 0x1F) >>> 0;
        this.str.tgt = ((instr >>> 14) & 0x1F) >>> 0;
        this.str.imm13 = ((instr >>> 19) & 0x1FFF) >>> 0;
    }
}

class funnyarchCPUInstrEncoding3 {
    constructor(instr) {
        this.instr = instr >>> 0;
        this.str = {};
        this.str.opcode = (instr & 0x3F) >>> 0;
        this.str.condition = ((instr >>> 6) & 0x07) >>> 0;
        this.str.tgt = ((instr >>> 9) & 0x1F) >>> 0;
        this.str.instr_spe = ((instr >>> 14) & 0x3) >>> 0;
        this.str.imm16 = ((instr >>> 16) & 0xFFFF) >>> 0;
    }
}

class funnyarchCPUInstrEncoding4 {
    constructor(instr) {
        this.instr = instr >>> 0;
        this.str = {};
        this.str.opcode = (instr & 0x3F) >>> 0;
        this.str.condition = ((instr >>> 6) & 0x07) >>> 0;
        this.str.imm23 = ((instr >>> 9) & 0x7FFFFF) >>> 0;
    }
}

class funnyarchCPUInstrEncoding5 {
    constructor(instr) {
        this.instr = instr >>> 0;
        this.str = {};
        this.str.opcode = (instr & 0x3F) >>> 0;
        this.str.condition = ((instr >>> 6) & 0x07) >>> 0;
        this.str.tgt = ((instr >>> 9) & 0x1F) >>> 0;
        this.str.instr_spe = ((instr >>> 14) & 0x3FFFF) >>> 0;
    }
}

class funnyarchCPUInstrEncoding6 {
    constructor(instr) {
        this.instr = instr >>> 0;
        this.str = {};
        this.str.opcode = (instr & 0x3F) >>> 0;
        this.str.condition = ((instr >>> 6) & 0x07) >>> 0;
        this.str.instr_spe = ((instr >>> 9) & 0x7FFFFF) >>> 0;
    }
}

class funnyarchCPUInstrEncoding7 {
    constructor(instr) {
        this.instr = instr >>> 0;
        this.str = {};
        this.str.opcode = (instr & 0x3F) >>> 0;
        this.str.condition = ((instr >>> 6) & 0x07) >>> 0;
        this.str.src = ((instr >>> 9) & 0x1F) >>> 0;
        this.str.tgt = ((instr >>> 14) & 0x1F) >>> 0;
        this.str.instr_spe = ((instr >>> 19) & 0x1FFF) >>> 0;
    }
}

function subtract_overflow(num1, num2) {
    let result = ((num1 >>> 0) - (num2 >>> 0)) >>> 0;
    let result2 = num1 - num2;
    return { "result": result, "carry": result2 != result };
}

function twosComplement(num, bits) {
    const maxNegVal = 2n ** BigInt(bits - 1);
    const maxUnsignedVal = 2n ** BigInt(bits);
    return Number(((BigInt(num) + maxNegVal) % maxUnsignedVal) - maxNegVal);
}

class funnyarchCPU {
    #REG_LR = 28;
    #REG_RIP = 30;
    #REG_RF = 31;
    #SYSREG_IRIP = 4
    #SYSREG_IBPTR = 5
    #SYSREG_PCST = 6
    #SYSREG_TLBIRIP = 7
    #SYSREG_TLBIPTR = 8
    #SYSREG_TLBFLT = 9

    #CPU_TLB_INDEX_BITS = 7
    #TLB_ENTRYCOUNT = (1 << this.#CPU_TLB_INDEX_BITS) >>> 0
    #TLB_INDEX_BITS_MASK = ((1 << this.#CPU_TLB_INDEX_BITS) - 1) >>> 0

    constructor(memRead, memWrite) {
        this.memRead = memRead;
        this.memWrite = memWrite;
        this.registers = new Uint32Array(32);
        this.sysregisters = new Uint32Array(10);
        this.tlb = new BigUint64Array(this.#TLB_ENTRYCOUNT);
        this.reset();
    }

    reset() {
        for (let i = 0; i < this.registers.length; i++) {
            this.registers[i] = 0;
        }
        for (let i = 0; i < this.sysregisters.length; i++) {
            this.sysregisters[i] = 0;
        }
    }


    pcst_push_state_stack() {
        this.sysregisters[this.#SYSREG_PCST] = ((this.sysregisters[this.#SYSREG_PCST] & 0xFFFFF000) >>> 0) | ((this.sysregisters[this.#SYSREG_PCST] & 0xF0) << 4) |
            ((this.sysregisters[this.#SYSREG_PCST] & 0xF) << 4) | (this.sysregisters[this.#SYSREG_PCST] & 0xF);
    }

    pcst_pop_state_stack() {
        this.sysregisters[this.#SYSREG_PCST] = ((this.sysregisters[this.#SYSREG_PCST] & 0xFFFFF000) >>> 0) | (this.sysregisters[this.#SYSREG_PCST] & 0xF00) |
            ((this.sysregisters[this.#SYSREG_PCST] & 0xF00) >>> 4) | ((this.sysregisters[this.#SYSREG_PCST] & 0xF0) >>> 4);
    }

    tlb_translate_memaddr(addr) {
        return ((this.sysregisters[this.#SYSREG_PCST] & 0b100) != 0) ? Number(((this.tlb[((addr >>> 12) & this.#TLB_INDEX_BITS_MASK) >>> 0] & BigInt(0xFFFFF)) << BigInt(12)) | (BigInt(addr) & BigInt(0xFFF)))
            : addr;
    }

    memaddr_in_tlb(addr) {
        if ((this.sysregisters[this.#SYSREG_PCST] & 0b100) != 0) {
            const tlbent = this.tlb[((addr >>> 12) & this.#TLB_INDEX_BITS_MASK) >>> 0];
            if (((tlbent & (BigInt(1) << BigInt(40))) != 0) && (((tlbent & (BigInt(0xFFFFF) << BigInt(20))) >> BigInt(20)) == (addr >>> 12))) {
                return true;
            }
            return false;
        }
        return true;
    }

    tlb_invalidate_addr(addr) {
        this.tlb[((addr >>> 12) & this.#TLB_INDEX_BITS_MASK) >>> 0] = this.tlb[((addr >>> 12) & this.#TLB_INDEX_BITS_MASK) >>> 0] & ~((BigInt(1) << BigInt(40)));
    }

    tlb_write_addr(vaddr, paddr) {
        vaddr >>>= 12;
        paddr >>>= 12;
        this.tlb[vaddr & this.#TLB_INDEX_BITS_MASK] = BigInt(paddr) | (BigInt(vaddr) << BigInt(20)) | (BigInt(1) << BigInt(40));
    }

    do_tlbmiss(addr, dec_rip) {
        this.pcst_push_state_stack();
        // save rip
        this.sysregisters[this.#SYSREG_TLBIRIP] = dec_rip ? (this.registers[this.#REG_RIP] - 4) : this.registers[this.#REG_RIP];
        this.sysregisters[this.#SYSREG_TLBFLT] = addr;
        // unset usermode, TLB and hardware interrupt bits
        this.sysregisters[this.#SYSREG_PCST] = this.sysregisters[this.#SYSREG_PCST] & ~0b1110;
        // jump
        this.registers[this.#REG_RIP] = (this.sysregisters[this.#SYSREG_TLBIPTR] & 0xFFFFFFFC) >>> 0;
    }

    interrupt(n) {
        this.pcst_push_state_stack();
        // save rip
        this.sysregisters[this.#SYSREG_IRIP] = this.registers[this.#REG_RIP];
        // set interrupt number in pcst
        this.sysregisters[this.#SYSREG_PCST] = ((this.sysregisters[this.#SYSREG_PCST] & 0x00FFFFFF) | (n & 0xFF) << 24) >>> 0;
        // unset usermode and hardware interrupt bits
        this.sysregisters[this.#SYSREG_PCST] = this.sysregisters[this.#SYSREG_PCST] & ~0b1010;
        // jump
        this.registers[this.#REG_RIP] = (((this.sysregisters[this.#SYSREG_IBPTR] & 0xFFFFFFFC) >>> 0) + (((this.sysregisters[this.#SYSREG_IBPTR] & 0b1) != 0) ? 0 : (4 * n))) >>> 0;
    }

    #shouldexecute(condition) {
        switch (condition) {
            default: // always
                return true;
            case 1: // if equal
                return (this.registers[this.#REG_RF] & 0b10) != 0;
            case 2: // if not equal
                return (this.registers[this.#REG_RF] & 0b10) == 0;
            case 3: // if less than
                return (this.registers[this.#REG_RF] & 0b01) != 0;
            case 4: // if greater than or equal
                return (this.registers[this.#REG_RF] & 0b01) == 0;
            case 5: // if greater than
                return (this.registers[this.#REG_RF] & 0b11) == 0;
            case 6: // if less than or equal
                return (this.registers[this.#REG_RF] & 0b11) != 0;
        }
    }

    execute(ninstrs) {
        while (ninstrs > 0) {
            ninstrs--;

            let instr = 0;
            if (this.memaddr_in_tlb((this.registers[this.#REG_RIP] & 0xFFFFFFFC) >>> 0)) {
                instr = this.memRead(this.tlb_translate_memaddr((this.registers[this.#REG_RIP] & 0xFFFFFFFC) >>> 0)) >>> 0;
            } else {
                this.do_tlbmiss((this.registers[this.#REG_RIP] & 0xFFFFFFFC) >>> 0, false);
                continue;
            }

            this.registers[this.#REG_RIP] += 4;

            let opcode = (instr & 0x3F) >>> 0;
            let cond = ((instr >>> 6) & 0x07) >>> 0;

            if (!this.#shouldexecute(cond)) {
                //console.log(`skipping ip: 0x${((this.registers[this.#REG_RIP] - 4) & 0xFFFFFFFC).toString(16)} istr: 0x${instr.toString(16)} opc: 0x${opcode.toString(16)}`);
                continue;
            }

            //console.log(`running ip: 0x${((this.registers[this.#REG_RIP] - 4) & 0xFFFFFFFC).toString(16)} istr: 0x${instr.toString(16)} opc: 0x${opcode.toString(16)}`);


            switch (opcode) {
                case 0x00: { /* NOP(E6) */
                    break;
                }

                case 0x01: { /* STRPI(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    e.str.imm13 = twosComplement(e.str.imm13, 13);
                    if (((this.sysregisters[this.#SYSREG_PCST] & 0b1) != 0) && (((this.registers[e.str.tgt] + e.str.imm13) & 0b11) != 0)) {
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(254);
                        break;
                    }
                    if (this.memaddr_in_tlb(this.registers[e.str.tgt] + e.str.imm13)) {
                        this.memWrite(this.tlb_translate_memaddr(this.registers[e.str.tgt] + e.str.imm13), this.registers[e.str.src]);
                    } else {
                        this.do_tlbmiss(this.registers[e.str.tgt] + e.str.imm13, true);
                        continue;
                    }
                    this.registers[e.str.tgt] += e.str.imm13;
                    break;
                }

                case 0x02: { /* JMP(E4) */
                    let e = new funnyarchCPUInstrEncoding4(instr);
                    this.registers[this.#REG_RIP] = e.str.imm23 * 4;
                    break;
                }

                case 0x03: { /* RJMP(E4) */
                    let e = new funnyarchCPUInstrEncoding4(instr);
                    this.registers[this.#REG_RIP] += twosComplement(e.str.imm23, 23) * 4;
                    break;
                }

                case 0x04: { /* MOV(E7) */
                    let e = new funnyarchCPUInstrEncoding7(instr);
                    this.registers[e.str.tgt] = this.registers[e.str.src];
                    break;
                }

                case 0x05: { /* MOV(E3) MOVH(E3) */
                    let e = new funnyarchCPUInstrEncoding3(instr);
                    if (e.str.instr_spe === 0b01) {
                        this.registers[e.str.tgt] = (this.registers[e.str.tgt] & 0xFFFF) | (e.str.imm16 << 16);
                    } else {
                        this.registers[e.str.tgt] = e.str.imm16;
                    }
                    break;
                }

                case 0x06: { /* LDR(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    e.str.imm13 = twosComplement(e.str.imm13, 13);
                    if (((this.sysregisters[this.#SYSREG_PCST] & 0b1) != 0) && (((this.registers[e.str.src] + e.str.imm13) & 0b11) != 0)) {
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(254);
                        break;
                    }
                    if (this.memaddr_in_tlb(this.registers[e.str.src] + e.str.imm13)) {
                        this.registers[e.str.tgt] = this.memRead(this.tlb_translate_memaddr(this.registers[e.str.src] + e.str.imm13));
                    } else {
                        this.do_tlbmiss(this.registers[e.str.src] + e.str.imm13, true);
                        continue;
                    }
                    break;
                }

                case 0x07: { /* LDRI(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    e.str.imm13 = twosComplement(e.str.imm13, 13);
                    if (((this.sysregisters[this.#SYSREG_PCST] & 0b1) != 0) && ((this.registers[e.str.src] & 0b11) != 0)) {
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(254);
                        break;
                    }
                    if (this.memaddr_in_tlb(this.registers[e.str.src])) {
                        this.registers[e.str.tgt] = this.memRead(this.tlb_translate_memaddr(this.registers[e.str.src]));
                    } else {
                        this.do_tlbmiss(this.registers[e.str.src], true);
                        continue;
                    }
                    this.registers[e.str.src] += e.str.imm13;
                    break;
                }

                case 0x08: { /* STR(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    e.str.imm13 = twosComplement(e.str.imm13, 13);
                    if (((this.sysregisters[this.#SYSREG_PCST] & 0b1) != 0) && (((this.registers[e.str.tgt] + e.str.imm13) & 0b11) != 0)) {
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(254);
                        break;
                    }
                    if (this.memaddr_in_tlb(this.registers[e.str.tgt] + e.str.imm13)) {
                        this.memWrite(this.tlb_translate_memaddr(this.registers[e.str.tgt] + e.str.imm13), this.registers[e.str.src]);
                    } else {
                        this.do_tlbmiss(this.registers[e.str.tgt] + e.str.imm13, true);
                        continue;
                    }
                    break;
                }

                case 0x09: { /* STRI(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    e.str.imm13 = twosComplement(e.str.imm13, 13);
                    if (((this.sysregisters[this.#SYSREG_PCST] & 0b1) != 0) && ((this.registers[e.str.tgt] & 0b11) != 0)) {
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(254);
                        break;
                    }
                    if (this.memaddr_in_tlb(this.registers[e.str.tgt])) {
                        this.memWrite(this.tlb_translate_memaddr(this.registers[e.str.tgt]), this.registers[e.str.src]);
                    } else {
                        this.do_tlbmiss(this.registers[e.str.tgt], true);
                        continue;
                    }
                    this.registers[e.str.tgt] += e.str.imm13;
                    break;
                }

                case 0x0a: { /* JAL(E4) */
                    let e = new funnyarchCPUInstrEncoding4(instr);
                    this.registers[this.#REG_LR] = this.registers[this.#REG_RIP];
                    this.registers[this.#REG_RIP] = e.str.imm23 * 4;
                    break;
                }

                case 0x0b: { /* RJAL(E4) */
                    let e = new funnyarchCPUInstrEncoding4(instr);
                    e.str.imm23 = twosComplement(e.str.imm23, 23);
                    this.registers[this.#REG_LR] = this.registers[this.#REG_RIP];
                    this.registers[this.#REG_RIP] += e.str.imm23 * 4;
                    break;
                }

                case 0x0c: { /* CMP(E7) */
                    let e = new funnyarchCPUInstrEncoding7(instr);
                    let res = subtract_overflow(this.registers[e.str.tgt], this.registers[e.str.src]);
                    this.registers[this.#REG_RF] = ((this.registers[this.#REG_RF] & 0xFFFFFFFE) | ((res.carry ? 1 : 0)) << 0) >>> 0;
                    this.registers[this.#REG_RF] = ((this.registers[this.#REG_RF] & 0xFFFFFFFD) | (((res.result == 0) ? 1 : 0) << 1)) >>> 0;
                    break;
                }

                case 0x0d: { /* CMP(E3) */
                    let e = new funnyarchCPUInstrEncoding3(instr);
                    let res = subtract_overflow(this.registers[e.str.tgt], e.str.imm16);
                    this.registers[this.#REG_RF] = ((this.registers[this.#REG_RF] & 0xFFFFFFFE) | ((res.carry ? 1 : 0)) << 0) >>> 0;
                    this.registers[this.#REG_RF] = ((this.registers[this.#REG_RF] & 0xFFFFFFFD) | (((res.result == 0) ? 1 : 0) << 1)) >>> 0;
                    break;
                }

                case 0x0e: { /* INT(E4) */
                    let e = new funnyarchCPUInstrEncoding4(instr);
                    let intn = e.str.imm23 & 0xFF;
                    // exceptions cannot be thrown with the int instruction
                    if (intn >= 253) {
                        this.registers[this.#REG_RIP] -= 4;
                        intn = 255;
                    }
                    this.interrupt(intn);
                    break;
                }

                case 0x10: { /* ADD(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = this.registers[e.str.src1] + this.registers[e.str.src2];
                    break;
                }

                case 0x11: { /* ADD(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = this.registers[e.str.src] + e.str.imm13;
                    break;
                }

                case 0x12: { /* ADD(E3) ADDH(E3) */
                    let e = new funnyarchCPUInstrEncoding3(instr);
                    if (e.str.instr_spe == 0b01) {
                        this.registers[e.str.tgt] += e.str.imm16 << 16;
                    } else {
                        this.registers[e.str.tgt] += e.str.imm16;
                    }
                    break;
                }

                case 0x13: { /* SUB(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = this.registers[e.str.src1] - this.registers[e.str.src2];
                    break;
                }

                case 0x14: { /* SUB(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = this.registers[e.str.src] - e.str.imm13;
                    break;
                }

                case 0x15: { /* SUB(E3) SUBH(E3) */
                    let e = new funnyarchCPUInstrEncoding3(instr);
                    if (e.str.instr_spe == 0b01) {
                        this.registers[e.str.tgt] -= e.str.imm16 << 16;
                    } else {
                        this.registers[e.str.tgt] -= e.str.imm16;
                    }
                    break;
                }

                case 0x16: { /* SHL(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src1] << (this.registers[e.str.src2] & 0b11111)) >>> 0;
                    break;
                }

                case 0x17: { /* SHL(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src] << (e.str.imm13 & 0b11111)) >>> 0;
                    break;
                }

                case 0x18: { /* SHR(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src1] >>> (this.registers[e.str.src2] & 0b11111)) >>> 0;
                    break;
                }

                case 0x19: { /* SHR(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src] >>> (e.str.imm13 & 0b11111)) >>> 0;
                    break;
                }

                case 0x1A: { /* SAR(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = twosComplement(this.registers[e.str.src1], 32) >> (this.registers[e.str.src2] & 0b11111);
                    break;
                }

                case 0x1B: { /* SAR(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = twosComplement(this.registers[e.str.src], 32) >> (e.str.imm13 & 0b11111);
                    break;
                }

                case 0x1C: { /* AND(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = this.registers[e.str.src1] & this.registers[e.str.src2];
                    break;
                }

                case 0x1D: { /* AND(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = this.registers[e.str.src] & e.str.imm13;
                    break;
                }

                case 0x1E: { /* AND(E3) ANDH(E3) */
                    let e = new funnyarchCPUInstrEncoding3(instr);
                    if (e.str.instr_spe == 0b01) {
                        this.registers[e.str.tgt] &= (e.str.imm16 << 16) >>> 0;
                    } else {
                        this.registers[e.str.tgt] &= e.str.imm16;
                    }
                    break;
                }

                case 0x1F: { /* OR(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src1] | this.registers[e.str.src2]) >>> 0;
                    break;
                }

                case 0x20: { /* OR(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src] | e.str.imm13) >>> 0;
                    break;
                }

                case 0x21: { /* OR(E3) ORH(E3) */
                    let e = new funnyarchCPUInstrEncoding3(instr);
                    if (e.str.instr_spe == 0b01) {
                        this.registers[e.str.tgt] |= (e.str.imm16 << 16) >>> 0;
                    } else {
                        this.registers[e.str.tgt] |= e.str.imm16;
                    }
                    break;
                }

                case 0x22: { /* XOR(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src1] ^ this.registers[e.str.src2]) >>> 0;
                    break;
                }

                case 0x23: { /* XOR(E2) */
                    let e = new funnyarchCPUInstrEncoding2(instr);
                    this.registers[e.str.tgt] = (this.registers[e.str.src] ^ e.str.imm13) >>> 0;
                    break;
                }

                case 0x24: { /* XOR(E3) XORH(E3) */
                    let e = new funnyarchCPUInstrEncoding3(instr);
                    if (e.str.instr_spe == 0b01) {
                        this.registers[e.str.tgt] ^= (e.str.imm16 << 16) >>> 0;
                    } else {
                        this.registers[e.str.tgt] ^= e.str.imm16;
                    }
                    break;
                }

                case 0x25: { /* NOT(E7) */
                    let e = new funnyarchCPUInstrEncoding7(instr);
                    this.registers[e.str.tgt] = (~this.registers[e.str.src]) >>> 0;
                    break;
                }

                case 0x26: { /* MTSR(E7) MFSR(E7) */
                    let e = new funnyarchCPUInstrEncoding7(instr);
                    if ((this.sysregisters[this.#SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(253);
                        break;
                    }
                    if (e.str.instr_spe == 1) { // MFSR
                        if (e.str.src >= 10) {
                            this.registers[this.#REG_RIP] -= 4;
                            this.interrupt(255);
                            break;
                        }
                        this.registers[e.str.tgt] = this.sysregisters[e.str.src];
                    } else { // MTSR
                        if (e.str.tgt >= 10) {
                            this.registers[this.#REG_RIP] -= 4;
                            this.interrupt(255);
                            break;
                        }
                        this.sysregisters[e.str.tgt] = this.registers[e.str.src];
                    }
                    break;
                }
                case 0x27: { /* INVLPG(E5) INVLTLB(E5) */
                    let e = new funnyarchCPUInstrEncoding5(instr);
                    if ((this.sysregisters[this.#SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(253);
                        break;
                    }
                    if (e.str.instr_spe == 1) { // INVLTLB
                        for (let i = 0; i < this.tlb.length; i++) {
                            this.tlb[i] = BigInt(0);
                        }
                    } else { // INVLPG
                        this.tlb_invalidate_addr(this.registers[e.str.tgt]);
                    }
                    break;
                }
                case 0x28: { /* TLBW(E1) */
                    let e = new funnyarchCPUInstrEncoding1(instr);
                    if ((this.sysregisters[this.#SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(253);
                        break;
                    }
                    this.tlb_write_addr(this.registers[e.str.src1], this.registers[e.str.tgt]);
                    break;
                }
                case 0x29: { /* IRET(E6) IRETTLB(E6) */
                    let e = new funnyarchCPUInstrEncoding6(instr);
                    if ((this.sysregisters[this.#SYSREG_PCST] & 0b10) != 0) { // instruction is not allowed in usermode
                        this.registers[this.#REG_RIP] -= 4;
                        this.interrupt(253);
                        break;
                    }
                    this.pcst_pop_state_stack();
                    this.registers[this.#REG_RIP] = (e.str.instr_spe == 1) ? this.sysregisters[this.#SYSREG_TLBIRIP] : this.sysregisters[this.#SYSREG_IRIP]; // IRETTLB?
                    break;
                }

                default: {
                    this.registers[this.#REG_RIP] -= 4;
                    this.interrupt(255);
                }
            }
        }
    }
}
