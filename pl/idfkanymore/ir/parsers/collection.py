from idfkanymore.parse import ast_mod
from .. import ir
from .. import lib as irlib
from .. import irgen as irgen
from . import expr

@irgen.reg_ast_node_parser((ast_mod.Assignment,), end_only=True)
def parse_assignment(ctx, node, bubble):
    ret = []
    if isinstance(node.to, ast_mod.Variable):
        var_name = node.to.name
        dst = ctx.proc_locals.get(var_name, None)
        is_local = True
        if dst is None:
            is_local = False
            dst = ctx.globalvars.get(var_name, None)
        irlib.assertion(dst is not None, f"variable with name {var_name} not found")
        if is_local:
            irlib.assertion(dst["kind"] == "var", "can only assign to variables")
        if is_local:
            dst_vreg = dst["regid"]
        else:
            dst_vreg = ctx.alloc_vreg(dst["type"])
        ret += expr.eval_expr(ctx, node.value, dst_vreg)
        if not is_local:
            tmp_vreg_ptr = ctx.alloc_vreg(ir.DatatypePointer(dst["type"]))
            tmp_vreg_idx = ctx.alloc_vreg(ctx.datatypes["USIZE"])
            ret += [
                ir.GetGlobalPtr(tmp_vreg_ptr, var_name),
                ir.SetRegImm(tmp_vreg_idx, 0),
                ir.SetPtrReg(tmp_vreg_ptr, tmp_vreg_idx, dst_vreg, dst["type"]),
            ]
    elif isinstance(node.to, ast_mod.PointerIndex):
        raise NotImplementedError("pointer assignment not yet supported")
    else:
        raise Exception("qwhar??")
    return ret
