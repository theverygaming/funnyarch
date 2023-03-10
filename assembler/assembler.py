import re

# instruction format:
# [number of arguments, opcode]
instructions = {
    "nop": [0, 0x01],
    "mov": [2, 0x02],
    "add": [2, 0x03],
    "jmp": [1, 0x13],
}

output = []

def write_out(bytes, num):
    num &= (1 << (bytes * 8)) - 1
    output.append(num.to_bytes(bytes, 'little'))

def getOperandType(op):
    val = 0
    optype = 0
    if len(op) == 0:
            raise Exception(f"invalid: {op}")
    if op.startswith("[") and op.endswith("]"): # pointer
        str = op.strip("[]")
        if len(str) == 0:
            raise Exception(f"invalid: {op}")
        if str[0] == 'r':
            optype = 1 # register pointer
            val = int(str.strip("r"), 0)
        else:
            optype = 3 # immediate pointer
            val = int(str, 0)
    elif op[0] == 'r':
        optype = 0 # register
        val = int(op.strip("r"))
    else: 
        optype = 2 # immediate
        val = int(op, 0)
    return val, optype

def parseInstr(line):
    split = re.split(" |,", line)
    split = list(filter(None, split))
    if len(split) == 0:
        return
    
    print("---")
    for s in split:
        print(f"    -> {s}")

    if split[0] not in instructions:
        raise Exception(f"invalid instruction {split[0]}")
    
    instrinfo = instructions[split[0]]

    if len(split) -1 != instrinfo[0]:
        raise Exception(f"invalid arg count for {split[0]} got {len(split) -1} want {instrinfo[0]}")

    control = instrinfo[1] & 0b1111111
    control |= (3 << 7) # operation size 64 bit

    operands = []
    for i in range(instrinfo[0]): # for operands
        val = getOperandType(split[1+i])
        operands.append(val)
        if i == 0: # source
            control |= (val[1] << 9) # set source type
        if i == 0: # target
            control |= (val[1] << 11) # set target type
    operands.reverse() # in the binary source comes first, in assembly target is first

    write_out(2, control) # write control

    for operand in operands:
        opsize = 8 # default 64-bit
        if operand[1] <= 1: # register
            opsize = 1
        write_out(opsize, operand[0])

f = open("test.asm")
for line in f.read().splitlines():
    parseInstr(line.lower())
f.close()

f = open("out.bin", "wb")
for byte in output:
    f.write(byte)
f.close()
