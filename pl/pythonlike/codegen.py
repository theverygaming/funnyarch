import json
import ir

def _c_str_esc(s):
    toescape = {
        # https://www.gnu.org/software/gnu-c-manual/gnu-c-manual.html#Character-Constants
        "\\": "\\\\",
        "?": "\\?",
        "'": "\\'",
        "\"": "\\\"",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "\v": "\\v",
    }
    esc = ""
    for c in s:
        if c not in toescape:
            esc += c
        else:
            esc += toescape[c]
    return esc

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

_default_type = "uintptr_t"

def _gen_asm_infunc(irl, global_syms):
    func_asm = ""
    func_used_regs = []

    def use_reg(regn):
        if regn not in func_used_regs:
            func_used_regs.append(regn)
    def use_global(globalname):
        if globalname not in global_syms:
            global_syms.append(globalname)

    def write_asm(s, indent=0):
        nonlocal func_asm
        func_asm += (" "*(indent+1)*2)+s

    for instr_idx, instr in enumerate(irl):
        write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.SetRegFuncArg):
            use_reg(instr.regn)
            write_asm(f"vreg_{instr.regn} = arg_{instr.argn};\n")
            continue
        if isinstance(instr, ir.SetRegGlobalPtr):
            use_reg(instr.regn)
            use_global(instr.globalname)
            write_asm(f"vreg_{instr.regn} = ({_default_type})&{instr.globalname};\n")
            continue
        if isinstance(instr, ir.ReadPointerReg):
            use_reg(instr.regn_ptr)
            use_reg(instr.regn_dst)
            use_reg(instr.regn_offset)
            write_asm(f"vreg_{instr.regn_dst} = (({_default_type} *)vreg_{instr.regn_ptr})[vreg_{instr.regn_offset}];\n")
            continue
        if isinstance(instr, ir.WritePointerReg):
            use_reg(instr.regn_ptr)
            use_reg(instr.regn_offset)
            use_reg(instr.regn_src)
            write_asm(f"(({_default_type} *)vreg_{instr.regn_ptr})[vreg_{instr.regn_offset}] = vreg_{instr.regn_src};\n")
            continue
        if isinstance(instr, ir.FuncReturnReg):
            write_asm(f"return vreg_{instr.regn};\n")
            continue
        if isinstance(instr, ir.FuncCall):
            if instr.return_regn:
                use_reg(instr.return_regn)
            args_def = ""
            args_regs = ""
            for n, argreg in enumerate(instr.arg_regns):
                args_def += f"{', ' if n != 0 else ''}{_default_type}"
                args_regs += f"{', ' if n != 0 else ''}vreg_{argreg}"
            use_global(instr.name)
            write_asm(f"{f'vreg_{instr.return_regn} = 'if instr.return_regn else ''}(({_default_type} (*)({args_def}))&{instr.name})({args_regs});\n")
            continue
        if isinstance(instr, ir.SetRegImm):
            use_reg(instr.regn)
            write_asm(f"vreg_{instr.regn} = {instr.value}u;\n")
            continue
        if isinstance(instr, ir.CopyReg):
            use_reg(instr.regn_dst)
            write_asm(f"vreg_{instr.regn_dst} = vreg_{instr.regn_src};\n")
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
    asm = ""
    func_name = None
    sym_defs = []
    global_syms = []

    def write_asm(s):
        nonlocal asm
        asm += s

    for instr_idx, instr in enumerate(irl):
        # write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.GlobalVarDef):
            sym_defs.append(instr.name)
            if isinstance(instr.value, str):
                write_asm(f'char {instr.name}[] = "{_c_str_esc(instr.value)}";\n')
            elif isinstance(instr.value, int):
                write_asm(f"{_default_type} {instr.name} = {instr.value};\n")
            else:
                raise Exception(
                    f"unknown variable type {type(instr.value)} while emitting global variable {instr.name}"
                )
            continue
        if isinstance(instr, ir.Function):
            sym_defs.append(instr.name)
            args = ""
            for n in range(instr.nargs):
                args += f"{', ' if n != 0 else ''}{_default_type} arg_{n}"
            write_asm(f"{_default_type} {instr.name}({args}) {{\n")
            #if instr.nlocals != 0:
            #    write_asm(f"  {_default_type} locals[{instr.nlocals}];\n")
            func_asm, func_used_regs = _gen_asm_infunc(instr.body, global_syms)
            
            for reg in func_used_regs:
                write_asm(f"  {_default_type} vreg_{reg};\n")
            
            asm += func_asm

            write_asm("  return -1; // return _some_ value so compiler does not complain\n}\n\n")
            continue
        raise Exception(f"unknown IR instruction {instr}")
    final_asm = "#include <stdint.h>\n\n"
    # generate globals
    nglobals = 0
    for gs in global_syms:
        if gs not in sym_defs:
            final_asm += f"extern {_default_type} {gs};\n"
            nglobals += 1
    if nglobals > 0:
        final_asm += "\n"
    return final_asm + asm
