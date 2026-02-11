from . import backends
from ..ir import ir


@backends.register_backend("funnyarch")
class BackendFunnyarch(backends.Backend):
    def _get_type_bytes(self, t):
        if isinstance(t, ir.DatatypeSimpleInteger):
            if t.bits % 8 != 0:
                raise Exception("invalid bit count")
            t_bytes = t.bits // 8
            return t_bytes
        elif isinstance(t, ir.DatatypePointer):
            return 4
        raise Exception(f"_get_type_bytes cannot handle {t}")

    def gen_assembly(self, irl):
        asm = ""

        def write_l(s):
            nonlocal asm
            asm += s + "\n"

        for inst in irl:
            write_l(f"// IR: {inst}")
            if isinstance(inst, ir.GlobalVarDef):
                write_l(f"{inst.name}:")
                if isinstance(inst.type_, ir.DatatypeSimpleInteger):
                    i_bytes = self._get_type_bytes(inst.type_)
                    for b in inst.value.to_bytes(i_bytes, "little", signed=inst.type_.signed):
                        write_l(f".byte 0x{b:x}")
                elif isinstance(inst.type_, ir.DatatypePointer):
                    for b in inst.value.to_bytes(4, "little", signed=False):
                        write_l(f".byte 0x{b:x}")
                elif isinstance(inst.type_, ir.DatatypeArray) and isinstance(inst.type_.item_type, ir.DatatypeSimpleInteger):
                    i_bytes = self._get_type_bytes(inst.type_.item_type)
                    for i in range(inst.type_.length):
                        for b in inst.value[i].to_bytes(i_bytes, "little", signed=inst.type_.item_type.signed):
                            write_l(f".byte 0x{b:x}")
                else:
                    raise Exception(f"encountered unknown datatype {inst.type_}")
            elif isinstance(inst, ir.Function):
                asm += self._gen_assembly_fn(inst)
                asm += "\n\n"
            else:
                raise Exception(f"unknown IR instr {inst}")
        return asm

    def _gen_assembly_fn(self, fn_inst):
        asm = ""

        def write_l(s):
            nonlocal asm
            asm += "  " + s + "\n"
        
        def fn_ret():
            write_l(f"rjmp .{fn_inst.name}_exit")

        def set_reg(reg, n_bytes, n):
            if n.bit_length() > n_bytes * 8:
                raise Exception("set_reg: number too large")
            write_l(f"mov {reg}, #{n & 0xFFFF}")
            if n.bit_length() / 8 > 2:
                write_l(f"movh {reg}, #{n >> 16}")

        # calling convention:
        # caller saves r0-r7 (arguments)
        # callee saves: r8-r26, rfp, lr
        # args passed in: r0-r7 and then on stack (first non-register argument is on top of stack)
        # return value in r0

        if len(fn_inst.args) > 8:
            raise Exception("stack arguments unsupported")

        # sometimes we need a temporary register, lets just permanently reserve one tehee :3
        tmpreg = "r26"

        # world's worst regalloc
        reg_map = {}
        _free_regs = [
            "r8","r9","r10","r11","r12","r13","r14","r15","r16","r17","r18","r19","r20","r21","r22","r23","r24","r25", #"r26"
        ]
        freeregs_idx = 0
        for id_ in fn_inst.regs:
            if freeregs_idx >= len(_free_regs):
                return f"// SKILL ISSUE: ran out of registers for function {fn_inst.name} (need {len(fn_inst.regs)}, got {len(_free_regs)} registers)"
                raise Exception(f"ran out of registers to use in fn {fn_inst.name} (need {len(fn_inst.regs)}, got {len(_free_regs)} registers)")
            reg_map[id_] = _free_regs[freeregs_idx]
            freeregs_idx += 1
        regs_callee_saved = list(reg_map.values()) + ["r26"]

        # function entry
        asm += f"{fn_inst.name}:\n"
        if not fn_inst.leaf:
            write_l("strpi rsp, lr, #-4")
        write_l("strpi rsp, rfp, #-4")
        write_l("mov rfp, rsp")
        for reg in regs_callee_saved:
            write_l(f"strpi rsp, {reg}, #-4")

        for inst in fn_inst.body:
            write_l(f"// IR: {inst}")
            if isinstance(inst, ir.SetRegImm):
                set_reg(reg_map[inst.regid], 4, inst.value)
            elif isinstance(inst, ir.LocalLabel):
                write_l(f".{fn_inst.name}_{inst.label}:")
            elif isinstance(inst, ir.GetArgVal):
                _arg_regs = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"]
                # FIXME: refine args layout, this is bullshit lmao.. Maybe make a dict of tuples name: (idx, type)?
                _arg_idx = [i for i, (name, t) in enumerate(fn_inst.args) if name == inst.arg_name][0]
                write_l(f"mov {reg_map[inst.regid_dst]}, {_arg_regs[_arg_idx]}")
            elif isinstance(inst, ir.CopyReg):
                write_l(f"mov {reg_map[inst.regid_dst]}, {reg_map[inst.regid_src]}")
            elif isinstance(inst, ir.GetPtrReg):
                write_l(f"mov {tmpreg}, {reg_map[inst.regid_index]}")

                # power of two multiplication
                t_bytes = self._get_type_bytes(inst.type_)
                if t_bytes & (t_bytes - 1) != 0:
                    raise Exception("GetPtrReg: type size not a power of two")
                toshift = t_bytes.bit_length() - 1
                if toshift != 0:
                    write_l(f"shl {tmpreg}, {tmpreg}, #{toshift}")

                write_l(f"add {tmpreg}, {reg_map[inst.regid_ptr]}, {tmpreg}")
                write_l(f"ldr {reg_map[inst.regid_value]}, {tmpreg}, #0")
                if t_bytes != 4:
                    set_reg(tmpreg, 4, (1 << (t_bytes*8))-1)
                    write_l(f"and {reg_map[inst.regid_value]}, {reg_map[inst.regid_value]}, {tmpreg}")
            elif isinstance(inst, ir.SetPtrReg):
                write_l(f"mov {tmpreg}, {reg_map[inst.regid_index]}")

                # power of two multiplication
                t_bytes = self._get_type_bytes(inst.type_)
                if t_bytes & (t_bytes - 1) != 0:
                    raise Exception("GetPtrReg: type size not a power of two")
                toshift = t_bytes.bit_length() - 1
                if toshift != 0:
                    write_l(f"shl {tmpreg}, {tmpreg}, #{toshift}")
                # FIXME: this overwrites data if the type is not 32-bit integer # BUG
                write_l(f"add {tmpreg}, {reg_map[inst.regid_ptr]}, {tmpreg}")
                write_l(f"str {tmpreg}, {reg_map[inst.regid_value]}, #0")
            elif isinstance(inst, ir.JumpLocalLabel):
                write_l(f"rjmp .{fn_inst.name}_{inst.label}")
            elif isinstance(inst, ir.JumpLocalLabelCondTruthy):
                write_l(f"cmp {reg_map[inst.cond_regid]}, #0")
                write_l(f"ifneq rjmp .{fn_inst.name}_{inst.label}")
            elif isinstance(inst, ir.JumpLocalLabelCondFalsy):
                write_l(f"cmp {reg_map[inst.cond_regid]}, #0")
                write_l(f"ifeq rjmp .{fn_inst.name}_{inst.label}")
            elif isinstance(inst, ir.BinOp):
                binop_inst_map = {
                    ir.BinaryOperator.ADD: "add",
                    ir.BinaryOperator.SUB: "sub",
                    #ir.BinaryOperator.MULT: "",
                    #ir.BinaryOperator.DIV: "",
                    #ir.BinaryOperator.MOD: "",
                    ir.BinaryOperator.LSHIFT: "shl",
                    ir.BinaryOperator.RSHIFT: "shr",
                    ir.BinaryOperator.OR: "or",
                    ir.BinaryOperator.XOR: "xor",
                    ir.BinaryOperator.AND: "and",
                }
                write_l(f"{binop_inst_map[inst.op]} {reg_map[inst.regid_result]}, {reg_map[inst.regid_rhs]}, {reg_map[inst.regid_lhs]}")
            elif isinstance(inst, ir.FuncReturn):
                write_l(f"mov r0, {reg_map[inst.regid_retval]}")
                fn_ret()
            elif isinstance(inst, (ir.GetGlobalPtr, ir.GetFnPtr)):
                write_l(f"mov {reg_map[inst.regid_ptr_dst]}, {inst.name}")
            elif isinstance(inst, ir.FuncCall):
                if inst.name is None:
                    raise Exception("function pointer calls not supported yet")
                _arg_regs = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"]
                regs_caller_save = _arg_regs[:max(len(fn_inst.args), len(inst.regids_args))]
                for reg in regs_caller_save:
                    write_l(f"strpi rsp, {reg}, #-4")
                for i, reg in enumerate(inst.regids_args):
                    write_l(f"mov {_arg_regs[i]}, {reg_map[reg]}")
                write_l(f"rjal {inst.name}")
                if inst.regid_return is not None:
                    write_l(f"mov {reg_map[inst.regid_return]}, r0")
                for reg in reversed(regs_caller_save):
                    write_l(f"ldri {reg}, rsp, #4")
            else:
                raise Exception(f"unknown IR instr {inst}")

        write_l(f".{fn_inst.name}_exit:")
        for reg in reversed(regs_callee_saved):
            write_l(f"ldri {reg}, rsp, #4")
        write_l("ldri rfp, rsp, #4")
        if not fn_inst.leaf:
            write_l("ldri lr, rsp, #4")
        write_l("mov rip, lr")

        return asm
