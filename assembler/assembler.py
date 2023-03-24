import re
import sys

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} input output")
    exit(1)

infile = None
outfile = None


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


def write_out(bytes, num):
    num &= (1 << (bytes * 8)) - 1
    outfile.write(num.to_bytes(bytes, "little"))


def getOperandType(op):
    val = 0
    optype = 0
    if len(op) == 0:
        raise Exception(f"invalid: {op}")
    if op.startswith("[") and op.endswith("]"):  # pointer
        str = op.strip("[]")
        if len(str) == 0:
            raise Exception(f"invalid: {op}")
        if str[0] == "r":
            optype = 1  # register pointer
            val = int(str.strip("r"), 0)
        else:
            optype = 3  # immediate pointer
            val = int(str, 0)
    elif op[0] == "r":
        optype = 0  # register
        val = int(op.strip("r"))
    else:
        optype = 2  # immediate
        val = int(op, 0)
    return val, optype


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
        write_out(opsize, instruction.src)

    if instruction.operandcount == 2:
        opsize = opsizen
        if instruction.tgttype <= 1:  # register
            opsize = 1
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
        inst.src, inst.srctype = getOperandType(split[1])
    elif operandcount == 2:
        inst.src, inst.srctype = getOperandType(split[2])
        inst.tgt, inst.tgttype = getOperandType(split[1])
    writeInstr(splitinst[0], inst)


def assemble_cond_instr(str):
    inst = assembled_instr()
    split = re.split(r" |, ", str)
    if split[0] not in conditionmap:
        raise Exception(f"invalid condition {split[0]}")
    inst.condition = conditionmap[split[0]]
    split.remove(split[0])
    return split[0], inst, split


rg_singledirective = r"^\.(global|string|byte)(?!:).*"  # matches ".directive"
rg_label = r"^[a-z.][A-Za-z0-9]*:$"  # matches "label:"
rg_instr0 = r"^[a-z][a-z]*(\.8|\.16|\.32|\.64)*$"  # matches "instr(.nn)"
rg_instr1 = r"^(?!(if(z|c|nz|nc|nzc|oc|zoc)))[a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9\[\]]*[a-z0-9\[\]]$"  # matches "instr(.nn) src"
rg_instr2 = r"^[a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9\[\]]*, [a-z0-9\[\]]*$"  # matches "instr(.nn) tgt, src"
rg_cinstr0 = r"^if(z|c|nz|nc|nzc|oc|zoc) [a-z0-9]*( |\.8|\.16|\.32|\.64)*$"  # matches "cond instr(.nn)"
rg_cinstr1 = r"^if(z|c|nz|nc|nzc|oc|zoc) [a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9\[\]]*[a-z0-9\[\]]$"  # matches "cond instr(.nn) src"
rg_cinstr2 = r"^if(z|c|nz|nc|nzc|oc|zoc) [a-z]*( |\.8|\.16|\.32|\.64) *[a-z0-9\[\]]*, [a-z0-9\[\]]*$"  # matches "cond instr(.nn) tgt, src"


def assembleinstr(str):
    if re.match(rg_singledirective, str):
        print("    -> single")
    elif re.match(rg_label, str):
        print("    -> label")
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
        raise Exception(f"invalid: {str}")


def isvalidasm(str):
    return (
        re.match(rg_singledirective, str)
        or re.match(rg_label, str)
        or re.match(rg_instr0, str)
        or re.match(rg_instr1, str)
        or re.match(rg_instr2, str)
        or re.match(rg_cinstr0, str)
        or re.match(rg_cinstr1, str)
        or re.match(rg_cinstr2, str)
    )


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


def preprocess(str):
    # remove all duplicate whitespaces outside quotes
    # https://stackoverflow.com/a/14549316
    parts = re.split(r"""("[^"]*"|'[^']*')""", str)
    parts[::2] = map(lambda s: " ".join(s.split()), parts[::2])  # outside quotes
    str = " ".join(parts)

    if not len(str) == 0 and not isvalidasm(str):
        raise Exception(f"invalid: {str}")

    return str


infile = open(sys.argv[1])

outfile = open(sys.argv[2], "wb")
infilec = c_comment_remover(infile.read())
infile.close()

for line in infilec.splitlines():
    line = preprocess(line)
    if len(line) == 0:
        continue
    assembleinstr(line)

outfile.close()
