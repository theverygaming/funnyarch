import ir

def _IrOp2COp(ir_op):
    transl = {
        "Operators.ADD": "+",
        "Operators.SUB": "-",
        "Operators.MULT": "*",
        "Operators.DIV": "/",
        "Operators.MOD": "%",
        "Operators.LSHIFT": "<<",
        "Operators.RSHIFT": ">>",
        "Operators.OR": "|",
        "Operators.XOR": "^",
        "Operators.AND": "&",
    }
    if str(ir_op) not in transl:
        raise Exception(f"cannot translate operator {ir_op}")
    return transl[str(ir_op)]

def _IrCmpOp2CCmpOp(ir_op):
    transl = {
        "CompareOperators.EQ": "==",
        "CompareOperators.NEQ": "!=",
        "CompareOperators.LT": "<",
        "CompareOperators.LTEQ": "<=",
        "CompareOperators.GT": ">",
        "CompareOperators.GTEQ": ">=",
    }
    if str(ir_op) not in transl:
        raise Exception(f"cannot translate operator {ir_op}")
    return transl[str(ir_op)]


def _gen_asm_infunc(irl):
    func_asm = ""
    func_used_regs = []

    def use_reg(regn):
        if regn not in func_used_regs:
            func_used_regs.append(regn)

    def write_asm(s, indent=0):
        nonlocal func_asm
        func_asm += (" "*(indent+1)*2)+s

    for instr_idx, instr in enumerate(irl):
        write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.SetRegFuncArg):
            use_reg(instr.regn)
            write_asm(f"vreg_{instr.regn} = arg_{instr.argn};\n")
            continue
        if isinstance(instr, ir.FuncReturnReg):
            write_asm(f"return vreg_{instr.regn};\n")
            continue
        if isinstance(instr, ir.FuncCall):
            write_asm(f"{instr.name}();\n")
            continue
        if isinstance(instr, ir.SetRegImm):
            use_reg(instr.regn)
            write_asm(f"vreg_{instr.regn} = {instr.value};\n")
            continue
        if isinstance(instr, ir.ThreeAddressInstr):
            use_reg(instr.result)
            use_reg(instr.arg1)
            use_reg(instr.arg2)
            write_asm(f"vreg_{instr.result} = vreg_{instr.arg1} {_IrOp2COp(instr.op)} vreg_{instr.arg2};\n")
            continue
        if isinstance(instr, ir.Compare):
            use_reg(instr.reg1)
            use_reg(instr.reg2)
            write_asm(f"if (vreg_{instr.reg1} {_IrCmpOp2CCmpOp(instr.op)} vreg_{instr.reg2}) {{\n")
            write_asm(f"goto {instr.lblIfTrue};\n", indent=1)
            write_asm(f"}}\n")
            write_asm(f"else {{\n")
            write_asm(f"goto {instr.lblIfFalse};\n", indent=1)
            write_asm(f"}}\n")
            continue
        if isinstance(instr, ir.LocalLabel):
            write_asm(f"{instr.label}:\n")
            continue
        if isinstance(instr, ir.JumpLocalLabel):
            write_asm(f"goto {instr.label};\n")
            continue
        raise Exception(f"unknown IR instruction {instr}")
    return (func_asm, func_used_regs)

def gen_assembly(irl):
    asm = "#include <stdint.h>\n\n"
    func_name = None

    def write_asm(s):
        nonlocal asm
        asm += s

    for instr_idx, instr in enumerate(irl):
        # write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.GlobalVarDef):
            if isinstance(instr.value, str):
                write_asm(f'const char *{instr.name} = "{instr.value}";\n')
            elif isinstance(instr.value, int):
                write_asm(f"uint32_t {instr.name} = {instr.value};\n")
            else:
                raise Exception(
                    f"unknown variable type {type(instr.value)} while emitting global variable {instr.name}"
                )
            continue
        if isinstance(instr, ir.Function):
            args = ""
            for n in range(instr.nargs):
                args += f"{', ' if n != 0 else ''}uint32_t arg_{n}"
            write_asm(f"uint32_t {instr.name}({args}) {{\n")
            #if instr.nlocals != 0:
            #    write_asm(f"  uint32_t locals[{instr.nlocals}];\n")
            func_asm, func_used_regs = _gen_asm_infunc(instr.body)
            
            for reg in func_used_regs:
                write_asm(f"  uint32_t vreg_{reg};\n")
            
            asm += func_asm

            write_asm("  return -1; // return _some_ value so compiler does not complain\n}\n\n")
            continue
        raise Exception(f"unknown IR instruction {instr}")
    return asm

