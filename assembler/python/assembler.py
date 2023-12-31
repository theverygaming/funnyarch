import os
import re
import sys
from enum import Enum
import preprocessor


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

    def isimm(self):
        return (
            self.value >= OperandType.imm13.value
            and self.value <= OperandType.imm23.value
        )

    def islabel(self):
        return (
            self.value >= OperandType.label.value
            and self.value <= OperandType.rellabel.value
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
}

regmap_alias = {}


class AssembledInstr:
    def __init__(self, type, opcode, condition, operands, instrspecific):
        self.type = type
        self.opcode = opcode
        self.condition = condition
        self.operands = operands
        self.instrspecific = instrspecific


class Relocation:
    def __init__(self, symname, valueloc, isrelative, divideval, shift_offset, bits):
        self.symname = symname
        self.valueloc = valueloc
        self.isrelative = isrelative
        self.divideval = divideval  # if symbol value should be divided by 4
        self.shift_offset = shift_offset
        self.bits = bits


class Symbol:
    def __init__(self, symname, location):
        self.symname = symname
        self.location = location


# globals
outfile = None

origin = 0
relocations = []
symbols = []


def read_out(bytes):
    return int.from_bytes(outfile.read(bytes), "little", signed=False)


def write_out(bytes, num):
    num &= (1 << (bytes * 8)) - 1
    outfile.write(num.to_bytes(bytes, "little"))


def align_outfile(alignment):
    n = 4 - (outfile.tell() % alignment)
    if n == 4:
        n = 0
    for _ in range(n):
        write_out(1, ord("f"))


def get_operand_type(opstr):
    def parseop(str):
        isreg = False
        islabel = False
        isrellabel = False
        if str in regmap:
            isreg = True
            rval = regmap[str]
        elif str in regmap_alias:
            isreg = True
            rval = regmap_alias[str]
        elif str[0] == "#":
            rval = int(str[1:], 0)
        else:
            rval = re.sub(".rel$", "", str)
            islabel = not str.endswith(".rel")
            isrellabel = str.endswith(".rel")
        return isreg, islabel, isrellabel, rval

    if len(opstr) == 0:
        raise Exception(f"invalid: {opstr}")

    isreg, islabel, isrellabel, val = parseop(opstr)
    if isreg:
        optype = OperandType.register
    elif isrellabel:
        optype = OperandType.rellabel
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
    return val, optype


def relocate():
    for reloc in relocations:
        if not any([x for x in symbols if x.symname == reloc.symname]):
            raise Exception(f'invalid symbol "{reloc.symname}"')
        symbol = [x for x in symbols if x.symname == reloc.symname][0]
        symloc = symbol.location + origin
        relocval = 0
        if reloc.isrelative:
            relocval = symloc - (reloc.valueloc + origin + 4)
        else:
            relocval = symloc
        if reloc.divideval:
            relocval = int(relocval / 4)  # depends on instruction..
            print("reloc div")
        print(f"reloc sym: {reloc.symname} val: {relocval}")
        if relocval > pow(2, reloc.bits):
            raise Exception(f"relocation does not fit")
        oldpos = outfile.tell()
        outfile.seek(reloc.valueloc)
        value = read_out(4)
        mask = (1 << reloc.bits) - 1
        value = (value & ~(mask << reloc.shift_offset)) | (
            (relocval & mask) << reloc.shift_offset
        )
        outfile.seek(reloc.valueloc)
        write_out(4, value)
        outfile.seek(oldpos)


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
    print(
        f"instr: {match.group('cond') + ' ' if cond != 0 else ''}{instr} {', '.join(args)}"
    )

    for i, v in enumerate(args):
        val, opt = get_operand_type(v)
        args[i] = (val, opt, opt)  # value, operand type, actual operand type

    instinfo = None
    for inst in instructions[instr]:
        if len(inst.operands) != len(args):
            continue
        invalid = False
        for i, opt in enumerate(args):
            if opt[1].islabel() and inst.operands[i].isimm():
                args[i] = (opt[0], opt[1], inst.operands[i])
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
                Relocation(
                    v[0],
                    outfile.tell(),
                    v[1] == OperandType.rellabel or instinfo.relsymimm,
                    instinfo.divsymimm,
                    shift_offset,
                    bits,
                )
            )

    instr_assembled = AssembledInstr(
        instinfo.type, instinfo.opcode, cond, args, instinfo.instrspecific
    )
    write_instr(instr_assembled)


def parse_assembler_directive(str):
    split = re.split(r" ", str)
    if split[0] == ".origin":
        global origin
        origin = int(split[1], 0)
    elif split[0] == ".string" or split[0] == ".ascii":
        assert str[len(split[0]) + 1] == '"', 'string must be enclosed in ""'
        assert str[len(str) - 2] == '"', 'string must be enclosed in ""'
        outfile.write(bytes(str[len(split[0]) + 2 : len(str) - 2], "ascii"))
        if split[0] == ".string":
            write_out(1, 0)  # null terminator
    elif split[0] == ".byte":
        write_out(1, int(split[1], 0))
    elif split[0] == ".align":
        align_outfile(int(split[1], 0))
    elif split[0] == ".regalias":
        assert split[1] in regmap, "alias register not in register map"
        regmap_alias[split[2]] = regmap[split[1]]
    elif split[0] == ".regaliasclear":
        regmap_alias.clear()
    else:
        raise Exception(f"unsupported: {split[0]}")


def parse_assembler_label(match):
    label = match.group("label")
    if any(x for x in symbols if x.symname == label):
        raise Exception(f"double symbol {label}")
    align_outfile(4)  # FIXME: this alignment stuff is SUPER broken!!!
    symbols.append(Symbol(label, outfile.tell()))
    print(f'label "{label}" at {outfile.tell()}')


rg_arg = r"[A-Za-z0-9#\-_.]+"
rg_instr = rf"^(?:(?P<cond>(?:{'|'.join(conditionmap.keys())})?) +)?(?P<instr>[a-z]+)(?: (?P<arg1>{rg_arg})(?:, (?P<arg2>{rg_arg})(?:, (?P<arg3>{rg_arg}))?)?)?$"

rg_directive = r"^\.(export|extern|string|ascii|byte|origin|align|regalias|regaliasclear)(?!:).*$"  # matches ".directive"
rg_label = r"^(?P<label>[A-Za-z0-9_.]+)\:$"  # matches "label:"


def assembleinstr(str):
    if re.match(rg_directive, str) is not None:
        parse_assembler_directive(str)
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


genregex()

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} input output")
    exit(1)

infile = open(sys.argv[1])
with open(sys.argv[1]) as infile:
    try:
        infilec = preprocessor.preprocess(
            infile.read(), os.path.dirname(os.path.realpath(sys.argv[1]))
        )
    except Exception as e:
        print(f"preprocessor error: {e}")
        exit(1)

outfile = open(sys.argv[2], "w+b")

for line in infilec.splitlines():
    if len(line) == 0:
        continue
    try:
        pos = outfile.tell()
        assembleinstr(line)
        print(f"<0x{pos:x}> {line}")
    except Exception as e:
        print(f'error: {e}\nline: "{line}"')
        exit(1)

try:
    relocate()
except Exception as e:
    print(f"error resolving symbols: {e}")
    exit(1)

outfile.close()
