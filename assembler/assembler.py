import re
import sys


class instruction:
    def __init__(self, name, operandcount, opcode, sizelist):
        self.name = name
        self.operandcount = operandcount
        self.opcode = opcode
        self.sizelist = sizelist


instructions = {
    "ud": instruction("ud", 0, 0x00, [8, 16, 32, 64]),
    "nop": instruction("nop", 0, 0x01, [8, 16, 32, 64]),
    "mov": instruction("mov", 2, 0x02, [8, 16, 32, 64]),
    "add": instruction("add", 2, 0x03, [8, 16, 32, 64]),
    "sub": instruction("sub", 2, 0x04, [8, 16, 32, 64]),
    "div": instruction("div", 2, 0x05, [8, 16, 32, 64]),
    "idiv": instruction("idiv", 2, 0x06, [8, 16, 32, 64]),
    "mul": instruction("mul", 2, 0x07, [8, 16, 32, 64]),
    "imul": instruction("imul", 2, 0x08, [8, 16, 32, 64]),
    "rem": instruction("rem", 2, 0x09, [8, 16, 32, 64]),
    "irem": instruction("irem", 2, 0x0A, [8, 16, 32, 64]),
    "shr": instruction("shr", 2, 0x0B, [8, 16, 32, 64]),
    "shl": instruction("shl", 2, 0x0C, [8, 16, 32, 64]),
    "sar": instruction("sar", 2, 0x0D, [8, 16, 32, 64]),
    "and": instruction("and", 2, 0x0E, [8, 16, 32, 64]),
    "or": instruction("or", 2, 0x0F, [8, 16, 32, 64]),
    "xor": instruction("xor", 2, 0x10, [8, 16, 32, 64]),
    "not": instruction("not", 2, 0x11, [8, 16, 32, 64]),
    "test": instruction("test", 2, 0x12, [8, 16, 32, 64]),
    "jmp": instruction("jmp", 1, 0x13, [64]),
    "rjmp": instruction("rjmp", 1, 0x14, [64]),
    "cmp": instruction("cmp", 2, 0x15, [8, 16, 32, 64]),
    "int": instruction("int", 1, 0x16, [8]),
    "iret": instruction("iret", 0, 0x17, [8, 16, 32, 64]),
    "wfi": instruction("wfi", 0, 0x18, [8, 16, 32, 64]),
    "invlpg": instruction("invlpg", 1, 0x19, [64]),
}

opsizemap = {
    "8": 0,
    "16": 1,
    "32": 2,
    "64": 3,
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


class assembled_instr:
    def __init__(self):
        self.opcode = None
        self.operandcount = None
        self.opsize = opsizemap["64"]
        self.srctype = 0
        self.tgttype = 0
        self.src = 0
        self.tgt = 0
        self.condition = conditionmap["always"]


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


def getOperandType(op, is_target_op, instinfo, inst):
    val = 0
    optype = 0

    def getopsizebytes():
        return int(
            int(list(opsizemap.keys())[list(opsizemap.values()).index(inst.opsize)]) / 8
        )

    def getoperandinfo(isptr):
        skipbytes = 2
        valuesize = 0
        if is_target_op:
            if inst.srctype <= 1:  # register (8 bit)
                skipbytes += 1
            elif inst.srctype == 3:
                skipbytes += 8
            elif inst.srctype == 2:
                skipbytes += getopsizebytes()
        if isptr:
            valuesize = 8
        else:
            valuesize = getopsizebytes()
        return (outfile.tell() + skipbytes), valuesize

    def addreloc(name, isptr, isrel):
        valueloc, valuesize = getoperandinfo(isptr)
        relocations.append(relocation(name, valueloc, valuesize, outfile.tell(), isrel))

    def parseop(str, isptr):
        rval = 0
        isreg = False
        if str in regmap:
            isreg = True
            rval = regmap[str]
        elif str[0] == "#":
            rval = int(str[1:], 0)
        else:
            rstr = re.sub(".rel$", "", str)
            addreloc(rstr, isptr, str.endswith(".rel"))
        return isreg, rval

    if len(op) == 0:
        raise Exception(f"invalid: {op}")
    if op.startswith("[") and op.endswith("]"):  # pointer
        str = op.strip("[]")
        if len(str) == 0:
            raise Exception(f"invalid: {op}")
        isreg, val = parseop(str, True)
        if isreg:
            optype = 1  # register pointer
        else:
            optype = 3  # immediate pointer
    else:
        isreg, val = parseop(op, False)
        if isreg:
            optype = 0  # register
        else:
            optype = 2  # immediate
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


def writeInstr(name, instruction):
    opsizenb = int(
        list(opsizemap.keys())[list(opsizemap.values()).index(instruction.opsize)]
    )
    opsizen = int(opsizenb / 8)

    if opsizenb not in instructions[name].sizelist:
        raise Exception(
            f"invalid operand size {opsizenb} for {name} valid: {instructions[name].sizelist}"
        )

    if instruction.operandcount != instructions[name].operandcount:
        raise Exception(
            f"invalid operand count {instruction.operandcount} for {name} valid: {instructions[name].operandcount}"
        )

    if instruction.tgttype == 2:
        raise Exception(f"cannot target immediate")

    control = instruction.opcode & 0b1111111
    control |= (instruction.opsize & 0b11) << 7
    control |= (instruction.srctype & 0b11) << 9
    control |= (instruction.tgttype & 0b11) << 11
    control |= (instruction.condition & 0b111) << 13
    write_out(2, control)

    if instruction.operandcount >= 1:
        opsize = opsizen
        if instruction.srctype <= 1:  # register
            opsize = 1
        if instruction.srctype == 3:  # immediate pointer
            opsize = 8
        write_out(opsize, instruction.src)
        if instruction.operandcount == 2:
            opsize = opsizen
            if instruction.tgttype <= 1:  # register
                opsize = 1
            if instruction.tgttype == 3:  # immediate pointer
                opsize = 8
            write_out(opsize, instruction.tgt)


def assemble_instr(str, operandcount, inst=None, split=None):
    if split == None:
        split = re.split(r" |, ", str)
    if inst == None:
        inst = assembled_instr()
    splitinst = split[0].split(".")

    if splitinst[0] not in instructions:
        raise Exception(f"invalid instruction {splitinst[0]}")

    instinfo = instructions[splitinst[0]]

    inst.opcode = instinfo.opcode
    inst.operandcount = operandcount
    if len(splitinst) == 2:
        inst.opsize = opsizemap[splitinst[1]]

    if operandcount == 1:
        inst.src, inst.srctype = getOperandType(split[1], False, instinfo, inst)
    elif operandcount == 2:
        inst.src, inst.srctype = getOperandType(split[2], False, instinfo, inst)
        inst.tgt, inst.tgttype = getOperandType(split[1], True, instinfo, inst)
    writeInstr(splitinst[0], inst)


def assemble_cond_instr(str):
    inst = assembled_instr()
    split = re.split(r" |, ", str)
    if split[0] not in conditionmap:
        raise Exception(f"invalid condition {split[0]}")
    inst.condition = conditionmap[split[0]]
    split.remove(split[0])
    return split[0], inst, split


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


rg_directive = r"^\.(export|extern|string|byte|origin)(?!:).*"  # matches ".directive"
rg_label = r"^[A-Za-z0-9_.][A-Za-z0-9_.]*:$"  # matches "label:"
rg_instr0 = r"^[a-z][a-z]*(\.8|\.16|\.32|\.64)*$"  # matches "instr(.nn)"
rg_instr1 = r"^(?!(if(z|c|nz|nc|nzc|oc|zoc)))[a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9#-_.\[\]]*[a-z0-9#-_.\[\]]$"  # matches "instr(.nn) src"
rg_instr2 = r"^[a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9#-_.\[\]]*, [a-z0-9#-_.\[\]]*$"  # matches "instr(.nn) tgt, src"
rg_cinstr0 = r"^if(z|c|nz|nc|nzc|oc|zoc) [a-z0-9]*( |\.8|\.16|\.32|\.64)*$"  # matches "cond instr(.nn)"
rg_cinstr1 = r"^if(z|c|nz|nc|nzc|oc|zoc) [a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9#-_.\[\]]*[a-z0-9#-_.\[\]]$"  # matches "cond instr(.nn) src"
rg_cinstr2 = r"^if(z|c|nz|nc|nzc|oc|zoc) [a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9#-_.\[\]]*, [a-z0-9#-_.\[\]]*$"  # matches "cond instr(.nn) tgt, src"


def assembleinstr(str):
    if re.match(rg_directive, str):
        parse_assembler_directive(str)
    elif re.match(rg_label, str):
        parse_assembler_label(str)
    elif re.match(rg_instr0, str):
        assemble_instr(str, 0)
    elif re.match(rg_instr1, str):
        assemble_instr(str, 1)
    elif re.match(rg_instr2, str):
        assemble_instr(str, 2)
    elif re.match(rg_cinstr0, str):
        a1, a2, a3 = assemble_cond_instr(str)
        assemble_instr(a1, 0, a2, a3)
    elif re.match(rg_cinstr1, str):
        a1, a2, a3 = assemble_cond_instr(str)
        assemble_instr(a1, 1, a2, a3)
    elif re.match(rg_cinstr2, str):
        a1, a2, a3 = assemble_cond_instr(str)
        assemble_instr(a1, 2, a2, a3)
    else:
        raise Exception(f"invalid instruction: {str}")


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
        print(f"{e}\n{line}")
        exit(1)

try:
    relocate()
except Exception as e:
    print(f"error resolving symbols: {e}")
    exit(1)

outfile.close()
