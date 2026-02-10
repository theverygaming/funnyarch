from . import backends
from ..ir import ir


@backends.register_backend("funnyarch")
class BackendFunnyarch(backends.Backend):
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
                    if inst.type_.bits % 8 != 0:
                        raise Exception("invalid bit count")
                    i_bytes = inst.type_.bits // 8
                    for b in inst.value.to_bytes(i_bytes, "little", signed=inst.type_.signed):
                        write_l(F".byte 0x{b:x}")
                elif isinstance(inst.type_, ir.DatatypePointer):
                    for b in inst.value.to_bytes(4, "little", signed=False):
                        write_l(F".byte 0x{b:x}")
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

        for inst in fn_inst.body:
            write_l(f"// IR: {inst}")
            # if isinstance(inst, ir.GlobalVarDef):
            # else:
            #     raise Exception(f"unknown IR instr {inst}")

        # TODO: this can be dead code, we should check if it is!
        write_l("mov rip, lr")

        return asm
