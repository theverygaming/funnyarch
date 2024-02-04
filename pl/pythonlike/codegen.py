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


def _gen_asm_infunc(irl, func_retlbl):
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
        if isinstance(instr, ir.FuncReturnConst):
            write_asm(f"returnval = {instr.value};\n")
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
        raise Exception(f"unknown IR instruction {instr}")
    return (func_asm, func_used_regs)

def gen_assembly(irl):
    asm = "#include <stdint.h>\n\n"
    func_name = None
    func_retlbl = None

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
            func_retlbl = f"{instr.name}_RETURN"
            write_asm(f"uint32_t {instr.name}() {{\n")
            #if instr.nlocals != 0:
            #    write_asm(f"  uint32_t locals[{instr.nlocals}];\n")
            func_asm, func_used_regs = _gen_asm_infunc(instr.body, func_retlbl)
            
            for reg in func_used_regs:
                write_asm(f"  uint32_t vreg_{reg};\n")
            
            write_asm(f"  uint32_t returnval;\n")
            
            asm += func_asm

            # return
            write_asm(f"  {func_retlbl}:\n")
            write_asm("  return returnval;\n}\n\n")
            continue
        raise Exception(f"unknown IR instruction {instr}")
    return asm

# TODO: optimisation: FuncReturnConst do not generate rjmp if already at end of function

