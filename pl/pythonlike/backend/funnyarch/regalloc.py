import ir.ir as ir


def _get_used_regs(irl):
    func_used_regs = []

    def use_reg(regn):
        if regn not in func_used_regs:
            func_used_regs.append(regn)

    for instr in irl:
        if isinstance(instr, ir.SetRegFuncArg):
            use_reg(instr.regn)
            continue
        if isinstance(instr, ir.SetRegGlobalPtr):
            use_reg(instr.regn)
            continue
        if isinstance(instr, ir.ReadPointerReg):
            use_reg(instr.regn_ptr)
            use_reg(instr.regn_dst)
            use_reg(instr.regn_offset)
            continue
        if isinstance(instr, ir.WritePointerReg):
            use_reg(instr.regn_ptr)
            use_reg(instr.regn_offset)
            use_reg(instr.regn_src)
            continue
        if isinstance(instr, ir.FuncCall):
            if instr.return_regn is not None:
                use_reg(instr.return_regn)
            continue
        if isinstance(instr, ir.SetRegImm):
            use_reg(instr.regn)
            continue
        if isinstance(instr, ir.CopyReg):
            use_reg(instr.regn_dst)
            continue
        if isinstance(instr, ir.ThreeAddressInstr):
            use_reg(instr.result)
            use_reg(instr.arg1)
            use_reg(instr.arg2)
            continue
        if isinstance(instr, ir.Compare):
            use_reg(instr.reg1)
            use_reg(instr.reg2)
            continue
    return func_used_regs

_free_regs = [
    "r8","r9","r10","r11","r12","r13","r14","r15","r16","r17","r18","r19","r20","r21","r22","r23","r24","r25","r26"
]

def run(_backend, irl):
    for instr in irl:
        if not isinstance(instr, ir.Function):
            continue
        stackregs = []
        regs = _get_used_regs(instr.body)
        if len(regs) > len(_free_regs):
            raise Exception(f"too many registers ({len(regs)} > {len(_free_regs)}), regalloc does not support registers on the stack currently")
    return irl
