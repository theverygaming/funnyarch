import ir

_callconv_reg_return = "r0"

def _gen_asm_infunc(irl, func_retlbl):
    func_asm = ""
    func_nretjmp = 0
    func_used_regs = []

    def allocate_tmpregs(number):
        if number > 32 - (8 + 5):
            raise Exception("impossible number of temporary registers requested")
        regs = []
        for n in range(number):
            reg = f"r{8+n}"
            regs.append(reg)
            if reg not in func_used_regs:
                func_used_regs.append(reg)
        return regs

    def deallocate_tmpregs(regs):
        pass

    def write_asm(s, indent=0):
        nonlocal func_asm
        func_asm += (" "*(indent+1)*2)+s

    for instr_idx, instr in enumerate(irl):
        write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.FuncReturnConst):
            write_asm(f"mov {_callconv_reg_return}, #{instr.value}\n")
            continue
        if isinstance(instr, ir.FuncCall):
            write_asm(f"rjal {instr.name}\n")
            continue
        if isinstance(instr, ir.SetLocalConst):
            tmpregs = allocate_tmpregs(1)
            write_asm(f"mov {tmpregs[0]}, #{instr.value}\n")
            write_asm(f"str rfp, {tmpregs[0]}, #{instr.localn * 4}\n")
            deallocate_tmpregs(tmpregs)
            continue
        raise Exception(f"unknown IR instruction {instr}")
    return (func_asm, func_nretjmp, func_used_regs)

def gen_assembly(irl):
    asm = ""
    func_name = None
    func_retlbl = None

    def write_asm(s):
        nonlocal asm
        asm += s

    for instr_idx, instr in enumerate(irl):
        # write_asm(f"// IR: {instr}\n")
        if isinstance(instr, ir.GlobalVarDef):
            if isinstance(instr.value, str):
                write_asm(f'{instr.name}:\n.string "{instr.value}"\n.align 4\n\n')
            elif isinstance(instr.value, int):
                write_asm(f"{instr.name}:\n")
                n = instr.value
                for _ in range(4):
                    write_asm(f".byte {n & 0xFF}\n")
                    n >>= 8
                if n != 0:
                    raise Exception(f"global variable {instr.name} value overflow")
                write_asm("\n")
            else:
                raise Exception(
                    f"unknown variable type {type(instr.value)} while emitting global variable {instr.name}"
                )
            continue
        if isinstance(instr, ir.Function):
            func_retlbl = f".{instr.name}_RETURN"
            write_asm(f"{instr.name}:\n")
            if not instr.leaf:
                write_asm("strpi rsp, lr, #-4\n")
            write_asm("strpi rsp, rfp, #-4\n")
            write_asm("mov rfp, rsp\n")
            if instr.nlocals != 0:
                write_asm(f"sub rsp, #{instr.nlocals * 4}\n")
            func_asm, func_nretjmp, func_used_regs = _gen_asm_infunc(instr.body, func_retlbl)
            
            # push callee-saved regs
            for reg in func_used_regs:
                write_asm(f"strpi rsp, {reg}, #-4\n")
            
            asm += func_asm

            # return 
            # pop calee-saved regs
            for reg in reversed(func_used_regs):
                write_asm(f"ldri {reg}, rsp, #4\n")

            if func_nretjmp != 0:
                write_asm(f"{func_retlbl}:\n")
            write_asm("mov rsp, rfp\n")
            write_asm("ldri rfp, rsp, #4\n")
            if not instr.leaf:
                write_asm("ldri lr, rsp, #4\n")
            write_asm("mov rip, lr\n\n")
            continue
        
        raise Exception(f"unknown IR instruction {instr}")
    return asm

# TODO: optimisation: FuncReturnConst do not generate rjmp if already at end of function

