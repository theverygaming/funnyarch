import re
import sys
from enum import Enum

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
        return self.value >= OperandType.imm13.value and self.value <= OperandType.imm23.value

    def islabel(self):
        return self.value >= OperandType.label.value and self.value <= OperandType.rellabel.value

    def immfits(self, imm):
        if self.value >= OperandType.imm13.value and self.value <= OperandType.imm23.value and imm.value >= OperandType.imm13.value and imm.value <= OperandType.imm23.value:
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
    def __init__(self, type, opcode, operands):
        self.type = type
        self.opcode = opcode
        self.operands = operands


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
    "nop": [Instruction(InstructionType.E6, 0x00, get_op_types(InstructionType.E6))],
    "jmp": [Instruction(InstructionType.E5, 0x01, get_op_types(InstructionType.E5)), Instruction(InstructionType.E4, 0x02, get_op_types(InstructionType.E4))],
    "rjmp": [Instruction(InstructionType.E4, 0x03, get_op_types(InstructionType.E4))],
    "mov": [Instruction(InstructionType.E7, 0x04, get_op_types(InstructionType.E7)), Instruction(InstructionType.E3, 0x05, get_op_types(InstructionType.E3))],
    "ldr": [Instruction(InstructionType.E2, 0x06, get_op_types(InstructionType.E2))],
    "ldri": [Instruction(InstructionType.E2, 0x07, get_op_types(InstructionType.E2))],
    "str": [Instruction(InstructionType.E2, 0x08, get_op_types(InstructionType.E2))],
    "stri": [Instruction(InstructionType.E2, 0x09, get_op_types(InstructionType.E2))],

    "add": [Instruction(InstructionType.E1, 0x10, get_op_types(InstructionType.E1)), Instruction(InstructionType.E2, 0x11, get_op_types(InstructionType.E2)), Instruction(InstructionType.E3, 0x12, get_op_types(InstructionType.E3))],
    "sub": [Instruction(InstructionType.E1, 0x13, get_op_types(InstructionType.E1)), Instruction(InstructionType.E2, 0x14, get_op_types(InstructionType.E2)), Instruction(InstructionType.E3, 0x15, get_op_types(InstructionType.E3))],
    
    
    # pseudoinstructions
}

conditionmap = {
    "always": 0,
    "ifz": 1,
    "ifnz": 2,
    "ifc": 3,
    "ifnc": 4,
    "ifnzc": 5,
    "ifzoc": 6,
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
    "r27": 27,
    "r28": 28,
    "r29": 29,
    "r30": 30,
    "r31": 31,
    "rip": 32,
    "rsp": 33,
    "rflags": 34,
    "risp": 35,
    "rsflags": 36,
    "rivt": 37,
    "rpd": 38,
}


class AssembledInstr:
    def __init__(self, type, opcode, condition, operands, instrspecific):
        self.type = type
        self.opcode = opcode
        self.condition = condition
        self.operands = operands
        self.instrspecific = instrspecific


class relocation:
    def __init__(self, symname, valueloc, valuesizebytes, relloc, isrelative):
        self.symname = symname
        self.valueloc = valueloc
        self.valuesizebytes = valuesizebytes
        self.relloc = relloc
        self.isrelative = isrelative


class symbol:
    def __init__(self, symname, location):
        self.symname = symname
        self.location = location


# globals
outfile = None

origin = 0
relocations = []
symbols = []


def write_out(bytes, num):
    num &= (1 << (bytes * 8)) - 1
    outfile.write(num.to_bytes(bytes, "little"))

def get_operand_type(opstr):
    def addreloc(name, isptr, isrel):
        valueloc, valuesize = getoperandinfo(isptr)
        relocations.append(relocation(name, valueloc, valuesize, outfile.tell(), isrel))

    def parseop(str, isptr):
        isreg = False
        islabel = False
        isrellabel = False
        if str in regmap:
            isreg = True
            rval = regmap[str]
        elif str[0] == "#":
            rval = int(str[1:], 0)
        else:
            rval = re.sub(".rel$", "", str)
            islabel = not str.endswith(".rel")
            isrellabel = str.endswith(".rel")
            #addreloc(rstr, isptr, str.endswith(".rel"))
        return isreg, islabel, isrellabel, rval

    if len(opstr) == 0:
        raise Exception(f"invalid: {opstr}")
    if opstr.startswith("[") and opstr.endswith("]"):  # pointer
        str = opstr.strip("[]")
        if len(str) == 0:
            raise Exception(f"invalid: {opstr}")
        isreg, islabel, isrellabel, val = parseop(str, True)
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
                if val <= pow(2, 13) -1:
                    optype = OperandType.imm13
                elif val <= pow(2, 16) -1:
                    optype = OperandType.imm16
                elif val <= pow(2, 23) -1:
                    optype = OperandType.imm23
                else:
                    raise Exception(f"larger than biggest possible immediate: {opstr}")
    else:
        isreg, islabel, isrellabel, val = parseop(opstr, False)
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
                if val <= pow(2, 13) -1:
                    optype = OperandType.imm13
                elif val <= pow(2, 16) -1:
                    optype = OperandType.imm16
                elif val <= pow(2, 23) -1:
                    optype = OperandType.imm23
                else:
                    raise Exception(f"larger than biggest possible immediate: {opstr}")
    return val, optype


def relocate():
    for reloc in relocations:
        if not any([x for x in symbols if x.symname == reloc.symname]):
            raise Exception(f"invalid symbol {reloc.symname}")
        symbol = [x for x in symbols if x.symname == reloc.symname][0]
        symloc = symbol.location + origin
        relocval = 0
        if reloc.isrelative:
            relocval = symloc - (reloc.relloc + origin)
        else:
            relocval = symloc
        oldpos = outfile.tell()
        outfile.seek(reloc.valueloc)
        write_out(reloc.valuesizebytes, relocval)
        outfile.seek(oldpos)


def write_instr(instr):
    print(instr.type)
    instrword = (instr.opcode & 0x3F) | ((instr.condition & 0x7) << 6)
    print(instrword)

    if instr.type == InstructionType.E1:
        instrword |= ((instr.operands[1][0] & 0x1F) << 9) # source1
        instrword |= ((instr.operands[2][0] & 0x1F) << 14) # source2
        instrword |= ((instr.operands[0][0] & 0x1F) << 19) # target
        instrword |= ((instr.instrspecific & 0xFF) << 24) # instr-specific
    elif instr.type == InstructionType.E2:
        instrword |= ((instr.operands[1][0] & 0x1F) << 9) # source
        instrword |= ((instr.operands[0][0] & 0x1F) << 14) # target
        instrword |= ((instr.operands[2][0] & 0x1FFF) << 19) # imm13
    elif instr.type == InstructionType.E3:
        instrword |= ((instr.operands[0][0] & 0x1F) << 9) # target
        instrword |= ((instr.instrspecific & 0x03) << 14) # instr-specific
        instrword |= ((instr.operands[1][0] & 0xFFFF) << 16) # imm16
    elif instr.type == InstructionType.E4:
        instrword |= ((instr.operands[0][0] & 0x7FFFFF) << 9) # imm23
    elif instr.type == InstructionType.E5:
        instrword |= ((instr.operands[0][0] & 0x1F) << 9) # target
        instrword |= ((instr.instrspecific & 0x3FFFF) << 14) # instr-specific
    elif instr.type == InstructionType.E6:
        instrword |= ((instr.instrspecific & 0x7FFFFF) << 9) # instr-specific
    elif instr.type == InstructionType.E7:
        instrword |= ((instr.operands[1][0] & 0x1F) << 9) # source
        instrword |= ((instr.operands[0][0] & 0x1F) << 14) # target
        instrword |= ((instr.instrspecific & 0x1FFF) << 19) # instr-specific
    else:
        raise Exception(f"UNSUPPORTED {instr.type}")

    print(instrword)
    write_out(4, instrword)

def assemble_instr(match):
    cond = conditionmap[match.group('cond')] if match.group('cond') is not None else 0
    instr = match.group('instr')
    args = list(filter(lambda f: f is not None, [match.group('arg1'), match.group('arg2'), match.group('arg3')]))
    if instr not in instructions:
        raise Exception(f"{instr} not in instruction list")
    print(f"instr: {match.group('cond') + ' ' if cond != 0 else ''}{instr} {', '.join(args)}")

    for i, v in enumerate(args):
        val, opt = get_operand_type(v)
        args[i] = (val, opt, opt) # value, operand type, actual operand type

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
    for arg in args:
        if arg[1].islabel():
            raise Exception(f"labels UNSUPPORTED {instr}")
    
    instr_assembled = AssembledInstr(instinfo.type, instinfo.opcode, cond, args, 0)
    write_instr(instr_assembled)



def parse_assembler_directive(str):
    split = re.split(r" ", str)
    if split[0] == ".origin":
        global origin
        origin = int(split[1], 0)
    elif split[0] == ".string":
        outfile.write(bytes(str[len(split[0]) + 1 :].replace('"', ""), "ascii"))
        write_out(1, 0)  # null terminator
    else:
        raise Exception(f"unsupported: {split[0]}")


def parse_assembler_label(str):
    split = re.split(r":", str)
    if any(x for x in symbols if x.symname == split[0]):
        raise Exception(f"double symbol {split[0]}")
    symbols.append(symbol(split[0], outfile.tell()))


rg_arg = r"[A-Za-z0-9#\-_.\[\]]+"
rg_instr = rf"^(?:(?P<cond>(?:{'|'.join(conditionmap.keys())})?) +)?(?P<instr>[a-z]+)(?: (?P<arg1>{rg_arg})(?:, (?P<arg2>{rg_arg})(?:, (?P<arg3>{rg_arg}))?)?)?$"

rg_directive = r"^\.(export|extern|string|byte|origin)(?!:).*"  # matches ".directive"
rg_label = r"^[A-Za-z0-9_.][A-Za-z0-9_.]*:$"  # matches "label:"

def assembleinstr(str):
    if re.match(rg_directive, str):
        parse_assembler_directive(str)
    elif re.match(rg_label, str):
        parse_assembler_label(str)
    match = re.match(rg_instr, str)
    if match is None:
        raise Exception(f"could not match instruction")
    assemble_instr(match)


def c_comment_remover(text):  # https://stackoverflow.com/a/241506
    def replacer(match):
        s = match.group(0)
        if s.startswith("/"):
            return " "
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE,
    )
    return re.sub(pattern, replacer, text)


def rmspaces(str):
    parts = re.split(r"""("[^"]*"|'[^']*')""", str)
    parts[::2] = map(lambda s: " ".join(s.split()), parts[::2])  # outside quotes
    return " ".join(parts)


def resolvemacros(str, macros_c):
    class macro_c:
        def __init__(self, name, args, content):
            self.name = name
            self.args = args  # [""]
            self.content = content

    mcount = 0
    lines = []
    macros_s = []

    ismacro = False
    for line in str.splitlines():
        line = rmspaces(line)
        if ismacro:
            if line[-1] == "\\":
                line = line[:-1] + "\n"
            else:
                ismacro = False
            macros_s[-1] += line
            continue
        else:
            split = re.split(r" ", line)
            if split[0] == "#define":
                if line[-1] == "\\":
                    line = line[:-1] + "\n"
                    ismacro = True
                macros_s.append(line)
                continue
        lines.append(line)

    for macro in macros_s:
        rg_macargs = r"(#define ([A-Za-z0-9._]*)\((([A-Za-z0-9]*(, )?)*)\) )(.*)"
        rg_macnoargs = r"(#define ([A-Za-z0-9._]*) )(.*)"
        if re.match(rg_macargs, macro, flags=re.DOTALL):
            content = re.sub(rg_macargs, r"\6", macro, flags=re.DOTALL)
            name = re.sub(rg_macargs, r"\2", macro, flags=re.DOTALL)
            args = re.split(r", ", re.sub(rg_macargs, r"\3", macro, flags=re.DOTALL))
            macros_c.append(macro_c(name, args, content))
        elif re.match(rg_macnoargs, macro, flags=re.DOTALL):
            content = re.sub(rg_macnoargs, r"\3", macro, flags=re.DOTALL)
            name = re.sub(rg_macnoargs, r"\2", macro, flags=re.DOTALL)
            macros_c.append(macro_c(name, [], content))
        else:
            raise Exception(f"invalid macro definition {macro}")

    for i, line in enumerate(lines):
        if len(line) == 0:
            continue
        for macro in macros_c:
            rg_macargs = r"\((([a-z0-9-_. \[\]]*(, )?)*)\)$"
            if re.match(macro.name + rg_macargs, line):
                if len(macro.args) == 0:
                    raise Exception(f"invalid use of macro {macro.name}: {line}")
                mcount += 1
                args = re.sub(macro.name + rg_macargs, r"\1", line).split(", ")
                if len(macro.args) != len(args):
                    raise Exception(f"invalid macro argc {line}")

                s_margs, s_args = zip(
                    *sorted(
                        zip(macro.args, args), key=lambda n: len(n[0]), reverse=True
                    )
                )

                lines[i] = macro.content
                for j, arg in enumerate(s_args):
                    lines[i] = lines[i].replace(s_margs[j], arg)

            elif macro.name == line:
                if len(macro.args) != 0:
                    raise Exception(f"invalid use of macro {macro.name}: {line}")
                mcount += 1
                lines[i] = macro.content

    str = "\n".join(lines)
    return mcount, str


def preprocess(str):
    macros_c = []
    while True:
        mcount, str = resolvemacros(str, macros_c)
        if mcount == 0:
            break

    lines = str.splitlines()
    for i, line in enumerate(lines):
        lines[i] = rmspaces(line)
    str = "\n".join(lines)

    return str


if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} input output")
    exit(1)

infile = open(sys.argv[1])

outfile = open(sys.argv[2], "wb")
infilec = c_comment_remover(infile.read())
infile.close()

try:
    infilec = preprocess(infilec)
except Exception as e:
    print(f"preprocessor error: {e}")
    exit(1)

for line in infilec.splitlines():
    if len(line) == 0:
        continue
    try:
        assembleinstr(line)
    except Exception as e:
        print(f"error: {e}\non: {line}")
        exit(1)

try:
    relocate()
except Exception as e:
    print(f"error resolving symbols: {e}")
    exit(1)

outfile.close()