import ast
import ir.ir as ir
import ir.lib as irlib


def gen_call(ctx, op, return_regn=None):
    irlib.assertion(len(op.keywords) == 0, "no kwargs supported")
    irlib.assert_instance(op.func, ast.Name, "weird function call")
    # builtins
    if op.func.id == "ord":
        irlib.assertion(
            return_regn is not None
            and len(op.args) == 1
            and isinstance(op.args[0], ast.Constant)
            and isinstance(op.args[0].value, str),
            "ord builtin used incorrectly",
        )
        return [ir.SetRegImm(return_regn, ord(op.args[0].value))]
    ctx.func_is_leaf = False
    argRegs = []
    argRegIr = []
    for arg in op.args:
        reg = ctx.alloc_vreg()
        argRegs.append(reg)
        argRegIr += irlib.gen_expr(ctx, reg, arg)
    if op.func.id in ctx.func_locals:
        n = ctx.func_locals[op.func.id]
    else:
        n = ctx.alloc_vreg()
        argRegIr.append(ir.SetRegGlobalPtr(n, op.func.id))
    return argRegIr + [ir.FuncCall(n, argRegs, return_regn)]
