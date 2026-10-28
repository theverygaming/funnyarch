#!/usr/bin/env python3
import os
import re
import sys
from enum import Enum
import preprocessor
import libobjfmt as objfmt


class InstructionType(Enum):
    E1 = 1
    E2 = 2
    E3 = 3
    E4 = 4
    E5 = 5
    E6 = 6
    E7 = 7


class OperandType(Enum):
    register = 1
    imm13 = 2
    imm16 = 3
    imm23 = 4
    label = 5
    rellabel = 6
    rellowlabel = 7
    relhighlabel = 8
    lowlabel = 9
    highlabel = 10

    def isimm(self):
        return (
            self.value >= OperandType.imm13.value
            and self.value <= OperandType.imm23.value
        )

    def islabel(self):
        return (
            self.value >= OperandType.label.value
            and self.value <= OperandType.highlabel.value
        )

    def immfits(self, imm):
        if (
            self.value >= OperandType.imm13.value
            and self.value <= OperandType.imm23.value
            and imm.value >= OperandType.imm13.value
            and imm.value <= OperandType.imm23.value
        ):
            return self.value >= imm.value
        else:
            return False

    def compat(self, other):
        if self.value == other.value:
            return True
        if self.isimm() and other.isimm():
            return self.immfits(other)
        return False


class Instruction:
    def __init__(
        self,
        type,
        opcode,
        operands=None,
        relsymimm=False,
        divsymimm=False,
        instrspecific=0,
    ):
        self.type = type  # instruction encoding type
        self.opcode = opcode
        self.operands = operands  # instruction operand types as array
        self.relsymimm = relsymimm  # if label immediate should be relative
        self.divsymimm = divsymimm  # if label immediate should be divided by 4
        if self.operands is None:
            self.operands = get_op_types(self.type)
        self.instrspecific = instrspecific


def get_op_types(instrtype):
    if instrtype == InstructionType.E1:
        return [OperandType.register, OperandType.register, OperandType.register]
    elif instrtype == InstructionType.E2:
        return [OperandType.register, OperandType.register, OperandType.imm13]
    elif instrtype == InstructionType.E3:
        return [OperandType.register, OperandType.imm16]
    elif instrtype == InstructionType.E4:
        return [OperandType.imm23]
    elif instrtype == InstructionType.E5:
        return [OperandType.register]
    elif instrtype == InstructionType.E6:
        return []
    elif instrtype == InstructionType.E7:
        return [OperandType.register, OperandType.register]


instructions = {
    # real instructions
    "nop": [Instruction(InstructionType.E6, 0x00)],
    "jmp": [
        Instruction(InstructionType.E4, 0x02, divsymimm=True),
    ],
    "rjmp": [Instruction(InstructionType.E4, 0x03, relsymimm=True, divsymimm=True)],
    "mov": [
        Instruction(InstructionType.E7, 0x04),
        Instruction(InstructionType.E3, 0x05),
    ],
    "movh": [
        Instruction(InstructionType.E3, 0x05, instrspecific=1),
    ],
    "ldr": [Instruction(InstructionType.E2, 0x06)],
    "ldri": [Instruction(InstructionType.E2, 0x07)],
    "str": [Instruction(InstructionType.E2, 0x08)],
    "stri": [Instruction(InstructionType.E2, 0x09)],
    "strpi": [Instruction(InstructionType.E2, 0x01)],
    "jal": [
        Instruction(InstructionType.E4, 0x0A, divsymimm=True),
    ],
    "rjal": [
        Instruction(InstructionType.E4, 0x0B, relsymimm=True, divsymimm=True),
    ],
    "cmp": [
        Instruction(InstructionType.E7, 0x0C),
        Instruction(InstructionType.E3, 0x0D),
    ],
    "cmps": [
        Instruction(InstructionType.E7, 0x0C, instrspecific=1),
        Instruction(InstructionType.E3, 0x0D, instrspecific=1),
    ],
    "int": [
        Instruction(InstructionType.E4, 0x0E),
    ],
    "add": [
        Instruction(InstructionType.E1, 0x10),
        Instruction(InstructionType.E2, 0x11),
        Instruction(InstructionType.E3, 0x12),
    ],
    "addh": [
        Instruction(InstructionType.E3, 0x12, instrspecific=1),
    ],
    "sub": [
        Instruction(InstructionType.E1, 0x13),
        Instruction(InstructionType.E2, 0x14),
        Instruction(InstructionType.E3, 0x15),
    ],
    "subh": [
        Instruction(InstructionType.E3, 0x15, instrspecific=1),
    ],
    "shl": [
        Instruction(InstructionType.E1, 0x16),
        Instruction(InstructionType.E2, 0x17),
    ],
    "shr": [
        Instruction(InstructionType.E1, 0x18),
        Instruction(InstructionType.E2, 0x19),
    ],
    "sar": [
        Instruction(InstructionType.E1, 0x1A),
        Instruction(InstructionType.E2, 0x1B),
    ],
    "and": [
        Instruction(InstructionType.E1, 0x1C),
        Instruction(InstructionType.E2, 0x1D),
        Instruction(InstructionType.E3, 0x1E),
    ],
    "andh": [
        Instruction(InstructionType.E3, 0x1E, instrspecific=1),
    ],
    "or": [
        Instruction(InstructionType.E1, 0x1F),
        Instruction(InstructionType.E2, 0x20),
        Instruction(InstructionType.E3, 0x21),
    ],
    "orh": [
        Instruction(InstructionType.E3, 0x21, instrspecific=1),
    ],
    "xor": [
        Instruction(InstructionType.E1, 0x22),
        Instruction(InstructionType.E2, 0x23),
        Instruction(InstructionType.E3, 0x24),
    ],
    "xorh": [
        Instruction(InstructionType.E3, 0x24, instrspecific=1),
    ],
    "not": [
        Instruction(InstructionType.E7, 0x25),
    ],
    "mtsr": [
        Instruction(InstructionType.E7, 0x26),
    ],
    "mfsr": [
        Instruction(InstructionType.E7, 0x26, instrspecific=1),
    ],
    "invlpg": [
        Instruction(InstructionType.E5, 0x27),
    ],
    "invltlb": [
        Instruction(InstructionType.E5, 0x27, instrspecific=1),
    ],
    "tlbw": [
        Instruction(InstructionType.E1, 0x28),
    ],
    "iret": [
        Instruction(InstructionType.E6, 0x29),
    ],
    "irettlb": [
        Instruction(InstructionType.E6, 0x29, instrspecific=1),
    ]
}

conditionmap = {
    "always": 0,
    "ifz": 1,
    "ifeq": 1,
    "ifnz": 2,
    "ifneq": 2,
    "ifc": 3,
    "iflt": 3,
    "ifnc": 4,
    "ifgteq": 4,
    "ifnzc": 5,
    "ifgt": 5,
    "ifzoc": 6,
    "iflteq": 6,
}

regmap = {
    "r0": 0,
    "r1": 1,
    "r2": 2,
    "r3": 3,
    "r4": 4,
    "r5": 5,
    "r6": 6,
    "r7": 7,
    "r8": 8,
    "r9": 9,
    "r10": 10,
    "r11": 11,
    "r12": 12,
    "r13": 13,
    "r14": 14,
    "r15": 15,
    "r16": 16,
    "r17": 17,
    "r18": 18,
    "r19": 19,
    "r20": 20,
    "r21": 21,
    "r22": 22,
    "r23": 23,
    "r24": 24,
    "r25": 25,
    "r26": 26,
    "rfp": 27,
    "lr": 28,
    "rsp": 29,
    "rip": 30,
    "rf": 31,
    "scr0": 0,
    "scr1": 1,
    "scr2": 2,
    "scr3": 3,
    "irip": 4,
    "ibptr": 5,
    "pcst": 6,
    "tlbirip": 7,
    "tlbiptr": 8,
    "tlbflt": 9,
}

regmap_alias = {}


class AssembledInstr:
    def __init__(self, type, opcode, condition, operands, instrspecific):
        self.type = type
        self.opcode = opcode
        self.condition = condition
        self.operands = operands
        self.instrspecific = instrspecific


# globals
outfile = None

sections = {
    ".text": objfmt.Section(bytearray()),
    ".rodata": objfmt.Section(bytearray()),
    ".data": objfmt.Section(bytearray()),
}

current_section = ".text"
relocations = []
symbols = {}
symbol_predefs = {}

def symbol_get_predef(symname):
    pd = {}
    if symname in symbol_predefs:
        pd = symbol_predefs[symname]
        del symbol_predefs[symname]
    return pd

def symbol_set_attr(symname, attr, val):
    if symname in symbols:
        setattr(symbols[symname], attr, val)
    elif symname in symbol_predefs:
        symbol_predefs[symname][attr] = val
    else:
        symbol_predefs[symname] = {
            attr: val,
        }

def set_section(name):
    global current_section
    current_section = name
    if name not in sections:
        sections[name] = objfmt.Section(bytearray())

def write_out_bytes(b):
    sections[current_section].data += b


def write_out(bytes, num):
    mask = (1 << (bytes * 8)) - 1
    if num & ~mask:
        raise Exception(f"asked to write {bytes}-byte number but got 0x{num:x} which doesn't fit!")
    write_out_bytes(num.to_bytes(bytes, "little"))


def align_outfile(alignment):
    n = 4 - (len(sections[current_section].data) % alignment)
    if n == 4:
        n = 0
    for _ in range(n):
        write_out(1, ord("f"))

REGXP_SYMNAME = r"[a-zA-Z0-9_\.]+"

def get_operand_type(opstr):
    def parseop(str):
        isreg = False
        islabel = False
        isrellabel = False
        islowlabel = False
        ishighlabel = False
        extra = None
        if str in regmap:
            isreg = True
            rval = regmap[str]
        elif str in regmap_alias:
            isreg = True
            rval = regmap_alias[str]
        elif str[0] == "#":
            rval = int(str[1:], 0)
        else:
            match = re.match(rf"^(?P<name>{REGXP_SYMNAME})(?P<offsmath>(?:(?:\+|-)(?:\d+))+)?$", re.sub(r"(?P<attr>\.rel|\.rel\.low|\.rel\.high|\.low|\.high)$", "", str))
            if match is None:
                raise Exception(f"could not match label {str}")
            isrellabel = str.endswith(".rel") or str.endswith(".rel.low") or str.endswith(".rel.high")
            islowlabel = str.endswith(".low")
            ishighlabel = str.endswith(".high")
            extra = (
                sum([
                    (({"+": 1, "-": -1}[m[0]]) * int(m[1]))
                    for m in re.findall(r"(\+|-)(\d+)", match.group("offsmath"))
                ]) if match.group("offsmath") is not None else 0
            )
            islabel = not (isrellabel or islowlabel or ishighlabel)
            rval = match.group("name")
        return isreg, islabel, isrellabel, islowlabel, ishighlabel, rval, extra

    if len(opstr) == 0:
        raise Exception(f"invalid: {opstr}")

    isreg, islabel, isrellabel, islowlabel, ishighlabel, val, extra = parseop(opstr)
    if isreg:
        optype = OperandType.register
    elif isrellabel and islowlabel:
        optype = OperandType.rellowlabel
    elif isrellabel and ishighlabel:
        optype = OperandType.relhighlabel
    elif isrellabel:
        optype = OperandType.rellabel
    elif islowlabel:
        optype = OperandType.lowlabel
    elif ishighlabel:
        optype = OperandType.highlabel
    elif islabel:
        optype = OperandType.label
    else:
        if val < 0:
            if val <= pow(2, 12):
                optype = OperandType.imm13
            elif val <= pow(2, 15):
                optype = OperandType.imm16
            elif val <= pow(2, 22):
                optype = OperandType.imm23
            else:
                raise Exception(f"larger than biggest possible immediate: {opstr}")
        else:
            if val <= pow(2, 13) - 1:
                optype = OperandType.imm13
            elif val <= pow(2, 16) - 1:
                optype = OperandType.imm16
            elif val <= pow(2, 23) - 1:
                optype = OperandType.imm23
            else:
                raise Exception(f"larger than biggest possible immediate: {opstr}")
    return val, optype, extra


def encoding_get_imm_location(encoding):
    # returns (shift, bits)
    if encoding == InstructionType.E1:
        return (0, 0)
    elif encoding == InstructionType.E2:
        return (19, 13)
    elif encoding == InstructionType.E3:
        return (16, 16)
    elif encoding == InstructionType.E4:
        return (9, 23)
    elif encoding == InstructionType.E5:
        return (0, 0)
    elif encoding == InstructionType.E6:
        return (0, 0)
    elif encoding == InstructionType.E7:
        return (0, 0)
    else:
        raise Exception(f"UNSUPPORTED {encoding}")


def write_instr(instr):
    instrword = (instr.opcode & 0x3F) | ((instr.condition & 0x7) << 6)

    if instr.type == InstructionType.E1:
        instrword |= (instr.operands[1][0] & 0x1F) << 9  # source1
        instrword |= (instr.operands[2][0] & 0x1F) << 14  # source2
        instrword |= (instr.operands[0][0] & 0x1F) << 19  # target
        instrword |= (instr.instrspecific & 0xFF) << 24  # instr-specific
    elif instr.type == InstructionType.E2:
        instrword |= (instr.operands[1][0] & 0x1F) << 9  # source
        instrword |= (instr.operands[0][0] & 0x1F) << 14  # target
        instrword |= (instr.operands[2][0] & 0x1FFF) << 19  # imm13
    elif instr.type == InstructionType.E3:
        instrword |= (instr.operands[0][0] & 0x1F) << 9  # target
        instrword |= (instr.instrspecific & 0x03) << 14  # instr-specific
        instrword |= (instr.operands[1][0] & 0xFFFF) << 16  # imm16
    elif instr.type == InstructionType.E4:
        instrword |= (instr.operands[0][0] & 0x7FFFFF) << 9  # imm23
    elif instr.type == InstructionType.E5:
        instrword |= (instr.operands[0][0] & 0x1F) << 9  # target
        instrword |= (instr.instrspecific & 0x3FFFF) << 14  # instr-specific
    elif instr.type == InstructionType.E6:
        instrword |= (instr.instrspecific & 0x7FFFFF) << 9  # instr-specific
    elif instr.type == InstructionType.E7:
        instrword |= (instr.operands[1][0] & 0x1F) << 9  # source
        instrword |= (instr.operands[0][0] & 0x1F) << 14  # target
        instrword |= (instr.instrspecific & 0x1FFF) << 19  # instr-specific
    else:
        raise Exception(f"UNSUPPORTED {instr.type}")

    align_outfile(4)
    write_out(4, instrword)


def assemble_instr(match):
    cond = conditionmap[match.group("cond")] if match.group("cond") is not None else 0
    instr = match.group("instr")
    args = list(
        filter(
            lambda f: f is not None,
            [match.group("arg1"), match.group("arg2"), match.group("arg3")],
        )
    )
    if instr not in instructions:
        raise Exception(f"{instr} not in instruction list")
    # print(
    #     f"instr: {match.group('cond') + ' ' if cond != 0 else ''}{instr} {', '.join(args)}"
    # )

    for i, v in enumerate(args):
        val, opt, extra = get_operand_type(v)
        args[i] = (val, opt, opt, extra)  # value, operand type, actual operand type

    instinfo = None
    for inst in instructions[instr]:
        if len(inst.operands) != len(args):
            continue
        invalid = False
        for i, opt in enumerate(args):
            if opt[1].islabel() and inst.operands[i].isimm():
                args[i] = (opt[0], opt[1], inst.operands[i], opt[3])
            elif not inst.operands[i].compat(opt[1]):
                invalid = True
                break
        if not invalid:
            instinfo = inst

    if instinfo is None:
        raise Exception(f"invalid operands for {instr}")

    # if we have a label create a relocation at this point
    for i, v in enumerate(args):
        if v[1].islabel():
            args[i] = (0, v[1], v[2])
            shift_offset, bits = encoding_get_imm_location(instinfo.type)
            relocations.append(
                objfmt.RelocationSymbol(
                    section=current_section,
                    section_offset=len(sections[current_section].data),
                    pre1_rshift=(
                        (16 if v[1] in [OperandType.highlabel, OperandType.relhighlabel] else None)
                        or (2 if instinfo.divsymimm else None) # >> 2 = divide by 4
                    ),
                    pre2_mask=0xFFFF if v[1] in [OperandType.lowlabel, OperandType.rellowlabel] else None,
                    dst_bits=bits,
                    dst_shift_offset=shift_offset,
                    symbol=v[0],
                    offset=v[3],
                    pcrel=v[1] in [OperandType.rellabel, OperandType.rellowlabel, OperandType.relhighlabel] or instinfo.relsymimm,
                )
            )

    instr_assembled = AssembledInstr(
        instinfo.type, instinfo.opcode, cond, args, instinfo.instrspecific
    )
    write_instr(instr_assembled)

def parse_assembler_directive(str, include_paths):
    def emit_const(s, nbytes):
        try:
            nums = [int(num, 0) for num in s.split(",")]
            for num in nums:
                write_out(nbytes, num)
            return
        except ValueError:
            pass
        match = re.match(rf"^(?P<name1>{REGXP_SYMNAME})(?:(?P<offsop>\-)(?P<name2>{REGXP_SYMNAME}))?$", s)
        if match is None:
            raise Exception(f"could not match const {s}")
        if match.group("name2") is not None:
            if match.group("offsop") != "-":
                raise Exception("unknown offset operator")
            relocations.append(
                objfmt.RelocationSymbolDiff(
                    section=current_section,
                    section_offset=len(sections[current_section].data),
                    pre1_rshift=None,
                    pre2_mask=None,
                    dst_bits=nbytes*8,
                    dst_shift_offset=None,
                    symbola=match.group("name1"),
                    symbolb=match.group("name2"),
                )
            )
        else:
            relocations.append(
                objfmt.RelocationSymbol(
                    section=current_section,
                    section_offset=len(sections[current_section].data),
                    pre1_rshift=None,
                    pre2_mask=None,
                    dst_bits=nbytes*8,
                    dst_shift_offset=None,
                    symbol=match.group("name1"),
                    offset=0,
                    pcrel=False,
                )
            )
        write_out(nbytes, 0)

    def unescape_ascii_string(s):
        # escape sequences from https://sourceware.org/binutils/docs/as/Strings.html
        bout = bytearray()
        i = 0
        while i < len(s):
            if s[i] != "\\":
                bout += bytes(s[i], "ascii")
                i += 1
                continue
            i += 1
            esc = s[i:]
            if len(esc) == 0:
                print(f"WARNING: escape sequence at end of string")
                continue
            simple_escapes = {
                "\\": b"\\", # literal backslash
                "b": b"\b", # backspace
                "f": b"\f", # form feed
                "n": b"\n", # newline
                "r": b"\r", # carriage return
                "t": b"\t", # tab
                "\"": b"\"", # double quote
            }
            if esc[0] in simple_escapes:
                bout += simple_escapes[esc[0]]
                i += 1
            elif (m := re.match(r"^(?:(?P<hex>(?:x|X)[0-9a-fA-F]+)|(?P<oct>[0-7]{3}))", esc)) is not None:
                if m.group("hex") is not None:
                    x = int(m.group("hex")[1:], 16)
                    i += len(m.group("hex"))
                else:
                    x = int(m.group("oct"), 8)
                    i += len(m.group("oct"))
                if x > 255:
                    raise Exception(f"invalid literal {x}")
                bout += bytes([x])
            else:
                # take as is
                print(f"WARNING: invalid escape sequence \\{esc[0]}")
                bout += bytes(esc[0], "ascii")
                i += 1
        return bout

    split = re.split(r" ", str)
    if split[0] == ".section":
        set_section(split[1])
    elif split[0] == ".string" or split[0] == ".ascii":
        out_str = str[len(split[0]) + 1:].strip()
        assert out_str[0] == '"', 'string must be enclosed in ""'
        assert out_str[-1] == '"', 'string must be enclosed in ""'
        out_str = out_str[1 : -1]
        out_bytes = unescape_ascii_string(out_str)
        write_out_bytes(out_bytes)
        if split[0] == ".string":
            write_out(1, 0)  # null terminator
    elif split[0] == ".byte":
        emit_const(split[1], 1)
    elif split[0] == ".halfword":
        emit_const(split[1], 2)
    elif split[0] == ".word":
        emit_const(split[1], 4)
    elif split[0] == ".align":
        align_outfile(int(split[1], 0))
    elif split[0] == ".regalias":
        assert split[1] in regmap, "alias register not in register map"
        regmap_alias[split[2]] = regmap[split[1]]
    elif split[0] == ".regaliasclear":
        regmap_alias.clear()
    elif split[0] == ".set":
        setexpr = " ".join(split[1:])
        m = re.match(rf"(?P<dst>{REGXP_SYMNAME}),\s*(?P<src>{REGXP_SYMNAME})", setexpr)
        if m is None:
            raise Exception(f"could not parse .set '{setexpr}' (supports only symbol alias)")
        symbols[m.group("dst")] = symbols[m.group("src")]
    elif split[0] == ".zero":
        for _ in range(int(split[1])):
            write_out(1, 0)
    elif split[0] == ".comm":
        split2 = [x.strip() for x in " ".join(split[1:]).split(",")]
        if split2[0] in symbols:
            raise Exception(f"symbol {split2[0]} redefined")
        # symbols[split2[0]] = objfmt.Symbol(
        #     **({
        #         "section": current_section,
        #         "section_offset": None,
        #         "local": True,
        #         "weak": False,
        #         "common": True,
        #         "common_size": int(split2[1]),
        #     } | symbol_get_predef(split2[0]))
        # )

        # HACK: simply insert common symbols and their reserved data as if they were normal symbols. The linker doesn't support them yet lol
        symbols[split2[0]] = objfmt.Symbol(
            **({
                "section": current_section,
                "section_offset": len(sections[current_section].data), 
                "local": True,
                "weak": False,
                "common": False,
                "common_size": None,
            } | symbol_get_predef(split2[0]))
        )
        write_out(int(split2[1]), 0)
    elif split[0] == ".weak":
        symbol_set_attr(split[1], "weak", True)
    elif split[0] == ".local":
        symbol_set_attr(split[1], "local", True)
    elif split[0] == ".global":
        symbol_set_attr(split[1], "local", False)
    elif split[0] == ".incbin":
        match = re.match(r"^\"(?P<name>[^\"]+)\"(?:,(?P<skip>\d+)(?:,(?P<count>\d+))?)?$", "".join(split[1:]))
        if match is None:
            raise Exception("invalid .incbin directive")
        data = None
        for path in include_paths:
            p = os.path.join(path, match.group("name"))
            if not os.path.isfile(p):
                continue
            with open(p, "rb") as f:
                f.seek(int(match.group("skip") or 0))
                data = f.read(int(match.group("count") or -1))
                break
        if data is None:
            raise Exception(".incbin file not found in include path")
        write_out_bytes(data)
    else:
        raise Exception(f"unsupported directive: {split[0]}")


def parse_assembler_label(match):
    label = match.group("label")
    if label in symbols:
        raise Exception(f"duplicate symbol {label}")
    align_outfile(4)  # FIXME: this alignment stuff is SUPER broken!!!
    symbols[label] = objfmt.Symbol(
        **({
            "section": current_section,
            "section_offset": len(sections[current_section].data), 
            "local": True,
            "weak": False,
            "common": False,
            "common_size": None,
        } | symbol_get_predef(label))
    )
    # print(f'label "{label}" at {current_section}.{len(sections[current_section].data)}')


rg_arg = r"[A-Za-z0-9#\-_.\+\-]+"
rg_instr = rf"^(?:(?P<cond>(?:{'|'.join(conditionmap.keys())})?) +)?(?P<instr>[a-z]+)(?: (?P<arg1>{rg_arg})(?:, (?P<arg2>{rg_arg})(?:, (?P<arg3>{rg_arg}))?)?)?$"

rg_directive = r"^\.(export|extern|string|ascii|byte|halfword|word|section|align|regalias|regaliasclear|set|zero|comm|local|weak|global|incbin)(?!:).*$"  # matches ".directive"
rg_label = r"^(?P<label>[A-Za-z0-9_.]+)\:$"  # matches "label:"


def assembleinstr(str, include_paths):
    if re.match(rg_directive, str) is not None:
        parse_assembler_directive(str, include_paths)
        return
    elif re.match(rg_label, str) is not None:
        parse_assembler_label(re.match(rg_label, str))
        return
    match = re.match(rg_instr, str)
    if match is None:
        raise Exception(f"could not match instruction")
    assemble_instr(match)


def genregex():
    print("conditions: ", end="")
    for key in list(conditionmap.keys())[:-1]:
        print(f"{key}|", end="")
    print(f"{list(conditionmap.keys())[-1]}")
    print("instructions: ", end="")
    for key in list(instructions.keys())[:-1]:
        print(f"{key}|", end="")
    print(f"{list(instructions.keys())[-1]}")
    print("registers: ", end="")
    for key in list(regmap.keys())[:-1]:
        print(f"{key}|", end="")
    print(f"{list(regmap.keys())[-1]}")

if __name__ == "__main__":
    # genregex()

    import argparse

    parser = argparse.ArgumentParser(description="Weird compiler")
    parser.add_argument(
        "-o", "--output", metavar="output", help="output file name", required=True, type=str
    )
    parser.add_argument("input", metavar="input", help="input file name", type=str)
    parser.add_argument("-I", "--includepath", metavar="includepath", help="include paths", type=str, nargs="+")
    args = parser.parse_args()

    include_paths = [os.path.dirname(os.path.realpath(args.input))] + (args.includepath or [])

    with open(args.input) as infile:
        try:
            infilec = preprocessor.preprocess(
                infile.read(), include_paths
            )
        except Exception as e:
            raise Exception("preprocessor error") from e

    for line in infilec.splitlines():
        if len(line) == 0:
            continue
        try:
            pos = len(sections[current_section].data)
            assembleinstr(line, include_paths)
            # print(f"<0x{pos:x}> {line}")
        except Exception as e:
            raise Exception(f'error on line: "{line}"') from e

    with open(args.output, "w+b") as f:
        objfmt.to_obj_file(sections, symbols, relocations, f)
