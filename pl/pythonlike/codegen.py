import ir

# funnyarch calling convention:
# caller saves r0-r7 (arguments)
# callee saves: r8-r31
# args passed in: r0-r7 and then on stack (last argument is on top of stack)
# return value in r0

_callconv_reg_return = "r0"


def gen_assembly(irl):
    asm = ""

    func_name = None
    func_retlbl = None
    func_nretjmp = 0

    for instr_idx, instr in enumerate(irl):
        def is_next_instr(type):
            if (instr_idx + 1) < len(irl):
                return isinstance(irl[instr_idx + 1], type)
            return False
        if isinstance(instr, ir.GlobalVarDef):
            if isinstance(instr.value, str):
                asm += f'{instr.name}:\n.string "{instr.value}"\n.align 4\n\n'
            elif isinstance(instr.value, int):
                asm += f'{instr.name}:\n'
                n = instr.value
                for _ in range(4):
                    asm += f".byte {n & 0xFF}\n"
                    n >>= 8
                if n != 0:
                    raise Exception(f"global variable {instr.name} value overflow")
                asm += "\n"
            else:
                raise Exception(f"unknown variable type {type(instr.value)} while emitting global variable {instr.name}")
            continue
        if isinstance(instr, ir.FuncReturnConst):
            asm += f"mov {_callconv_reg_return}, #{instr.value}\n"
            if not is_next_instr(ir.FuncEnd):
                asm += f"rjmp {func_retlbl}\n"
                func_nretjmp += 1
            continue
        if isinstance(instr, ir.FuncBegin):
            func_name = instr.name
            func_retlbl = f".{func_name}_RETURN"
            func_nretjmp = 0
            asm += f"{instr.name}:\n"
            if not instr.leaf:
                asm += "strpi rsp, lr, #-4\n"
            continue
        if isinstance(instr, ir.FuncEnd):
            if func_nretjmp != 0:
                asm += f"{func_retlbl}:\n"
            if not instr.leaf:
                asm += "ldri lr, rsp, #4\n"
            asm += "mov rip, lr\n\n"
            continue
        if isinstance(instr, ir.FuncCall):
            asm += f"rjal {instr.name}\n"
            continue
        
        raise Exception(f"unknown IR instruction {instr}")
    return asm
