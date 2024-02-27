import ast
from random import random
import ir.ir as ir
import ir.lib as irlib


def gen_expr(ctx, result, op):
    if isinstance(op, ast.Constant):
        if isinstance(op.value, int):
            return [ ir.SetRegImm(result, op.value) ]
        if isinstance(op.value, str):
            ctx._global_counter += 1
            name = f"__compiler_global_{ctx._global_counter}_{int(random()*1000000000)}" # FIXME: this definitely isn't a great solution lol, we need non-exported globals
            ctx.globalvars[name] = [op.value]
            return [ ir.SetRegGlobalPtr(result, name) ]
        else:
            irlib.assertion(False, "unsupported constant type")
    if isinstance(op, ast.Name): # variable copy
        irlib.assertion(op.id in ctx.func_locals, f"undefined variable {op.id}")
        return [ ir.CopyReg(ctx.func_locals[op.id], result) ]
    if isinstance(op, ast.Call):
        return irlib.gen_call(ctx, op, result)
    if isinstance(op, ast.Subscript):
        irlib.assertion(op.value.id in ctx.func_locals, f"undefined variable {op.value.id}")
        regn_src = ctx.func_locals[op.value.id]
        regn_offset = ctx.alloc_vreg()
        return gen_expr(ctx, regn_offset, op.slice) + [ ir.ReadPointerReg(regn_src, result, regn_offset) ]
    irlib.assert_instance(op, ast.BinOp, f"unsupported expr {ast.dump(op)}")
    ops = [] # tuple[list[ir], int[vregn]]
    for x in [op.left, op.right]:
        if isinstance(x, ast.Name):
            irlib.assertion(x.id in ctx.func_locals, f"undefined variable {x.id}")
            ops.append(([], ctx.func_locals[x.id]))
            continue
        outn = ctx.alloc_vreg()
        ops.append((gen_expr(ctx, outn, x), outn))
    return ops[0][0] + ops[1][0] + [ ir.ThreeAddressInstr(result, ops[0][1], ops[1][1], ir.astOp2IrOp(op.op)) ]
