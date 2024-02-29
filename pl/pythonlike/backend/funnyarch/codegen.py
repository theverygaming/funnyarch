from . import regalloc

import ir.ir as ir


def to_asm_str(s):
    ret = ""
    for c in s:
        ret += f".byte {ord(c)}\n"
    ret += ".align 4\n\n"
    return ret


def _IrOp2Instr(ir_op):
    transl = {
        "Operators.ADD": "add",
        "Operators.SUB": "sub",
        "Operators.MULT": "mult",
        "Operators.DIV": "div",
        "Operators.MOD": "mod",
        "Operators.LSHIFT": "shl",
        "Operators.RSHIFT": "shr",
        "Operators.OR": "or",
        "Operators.XOR": "xor",
        "Operators.AND": "and",
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
        func_asm += (" " * (indent + 1) * 2) + s

    for instr in irl:
        write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.SetRegFuncArg):
            use_reg(instr.regn)
            write_asm(f"// TODO: mov r{instr.regn}, fn arg {instr.argn}\n")
            continue
        if isinstance(instr, ir.SetRegGlobalPtr):
            use_reg(instr.regn)
            use_global(instr.globalname)
            write_asm(f"// TODO: r{instr.regn} = ({_default_type})&{instr.globalname}\n")
            continue
        if isinstance(instr, ir.ReadPointerReg):
            use_reg(instr.regn_ptr)
            use_reg(instr.regn_dst)
            use_reg(instr.regn_offset)
            write_asm(
                f"ldr r{instr.regn_dst}, r{instr.regn_ptr}, #0 // TODO: offset in r{instr.regn_offset}\n"
            )
            continue
        if isinstance(instr, ir.WritePointerReg):
            use_reg(instr.regn_ptr)
            use_reg(instr.regn_offset)
            use_reg(instr.regn_src)
            write_asm(
                f"(({_default_type} *)vreg_{instr.regn_ptr})[vreg_{instr.regn_offset}] = vreg_{instr.regn_src};\n"
            )
            continue
        if isinstance(instr, ir.FuncReturnReg):
            write_asm(f"mov r0, r{instr.regn}\n")
            write_asm(f"// TODO: rjmp fn_end_label\n")
            continue
        if isinstance(instr, ir.FuncCall):
            if instr.return_regn is not None:
                use_reg(instr.return_regn)
            args_def = ""
            args_regs = ""
            for n, argreg in enumerate(instr.arg_regns):
                args_def += f"{', ' if n != 0 else ''}{_default_type}"
                args_regs += f"{', ' if n != 0 else ''}vreg_{argreg}"
            write_asm(
                f"{f'vreg_{instr.return_regn} = 'if instr.return_regn is not None else ''}(({_default_type} (*)({args_def}))vreg_{instr.regn})({args_regs});\n"
            )
            continue
        if isinstance(instr, ir.SetRegImm):
            use_reg(instr.regn)
            write_asm(f"mov r{instr.regn}, #{instr.value & 0xFFFF}\n")
            instr.value >>= 16
            if instr.value != 0:
                write_asm(f"movh r{instr.regn}, #{instr.value & 0xFFFF}\n")
            instr.value >>= 16
            if instr.value != 0:
                raise Exception("cannot fit number into register")
            continue
        if isinstance(instr, ir.CopyReg):
            use_reg(instr.regn_dst)
            write_asm(f"mov r{instr.regn_dst}, r{instr.regn_src}\n")
            continue
        if isinstance(instr, ir.ThreeAddressInstr):
            use_reg(instr.result)
            use_reg(instr.arg1)
            use_reg(instr.arg2)
            write_asm(
                f"{_IrOp2Instr(instr.op)} r{instr.result}, r{instr.arg1}, r{instr.arg2}\n"
            )
            continue
        if isinstance(instr, ir.Compare):
            use_reg(instr.reg1)
            use_reg(instr.reg2)
            write_asm(
                f"if (vreg_{instr.reg1} {_IrCmpOp2CCmpOp(instr.op)} vreg_{instr.reg2}) {{\n"
            )
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


def gen_assembly(backend, irl):
    regalloc.run(backend, irl)
    asm = ""
    sym_defs = []
    global_syms = []

    def write_asm(s):
        nonlocal asm
        asm += s

    for instr in irl:
        # write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.GlobalVarDef):
            sym_defs.append(instr.name)
            if len(instr.values) == 1:
                if isinstance(instr.values[0], str):
                    write_asm(f"{instr.name}:\n{to_asm_str(instr.values[0])}")
                elif isinstance(instr.values[0], int):
                    write_asm(f"{_default_type} {instr.name} = {instr.values[0]};\n")
                else:
                    raise Exception(
                        f"unknown variable type {type(instr.value)} while emitting global variable {instr.name}"
                    )
            else:
                write_asm(f"{_default_type} {instr.name}[] = {{\n")
                for i, val in enumerate(instr.values):
                    if not isinstance(val, int):
                        raise Exception(
                            f"unknown variable type {type(val)} while emitting global array {instr.name}"
                        )
                    write_asm(f"{', ' if i != 0 else ''}{val}")
                write_asm(f"}};\n")
            continue
        if isinstance(instr, ir.Function):
            sym_defs.append(instr.name)
            write_asm(f"{instr.name}:\n")
            func_asm, func_used_regs = _gen_asm_infunc(instr.body, global_syms)

            for reg in func_used_regs:
                write_asm(f"// uses: r{reg}\n")

            asm += func_asm

            write_asm(
                "  mov rip, lr\n\n"
            )
            continue
        raise Exception(f"unknown IR instruction {instr}")
    final_asm = ".origin 0x0\nrjmp _start\n\n"
    # generate globals
    nglobals = 0
    for gs in global_syms:
        if gs not in sym_defs:
            final_asm += f"extern {_default_type} {gs}[];\n"
            nglobals += 1
    if nglobals > 0:
        final_asm += "\n"
    return final_asm + asm
