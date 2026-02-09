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
                else:
                    raise Exception(f"encountered unknown datatype {inst.type_}")
                continue
            raise Exception(f"unknown IR instr {inst}")
        return asm
