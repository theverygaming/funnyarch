from idfkanymore.parse import ast_mod
from .. import ir
from .. import lib as irlib
from .. import irgen as irgen

def find_variable(ctx, name):
    val = ctx.proc_locals.get(name, None)
    if val is not None:
        return {
            "type": val["kind"],
            "val": val,
        }
    val = ctx.globalvars.get(name, None)
    if val is not None:
        return {
            "type": "global",
            "val": val,
        }
    irlib.assertion(False, f"variable with name {name} not found")

def eval_expr(ctx, expr, dest_vreg_id):
    if isinstance(expr, ast_mod.Constant) and isinstance(expr.value, int):
        return [ir.SetRegImm(dest_vreg_id, expr.value)]
    elif isinstance(expr, ast_mod.Variable):
        var_found = find_variable(ctx, expr.name)
        match var_found["type"]:
            case "var":
                return [ir.CopyReg(var_found["val"]["regid"], dest_vreg_id)]
            case "arg":
                return [ir.GetArgVal(dest_vreg_id, expr.name)]
            case "global":
                tmp_vreg_ptr = ctx.alloc_vreg(ir.DatatypePointer(var_found["val"]["type"]))
                tmp_vreg_idx = ctx.alloc_vreg(ctx.datatypes["USIZE"])
                return [
                    ir.GetGlobalPtr(tmp_vreg_ptr, expr.name),
                    ir.SetRegImm(tmp_vreg_idx, 0),
                    ir.SetPtrReg(tmp_vreg_ptr, tmp_vreg_idx, dest_vreg_id, var_found["val"]["type"]),
                ]
    elif isinstance(expr, ast_mod.Binop):
        tmp_vreg_lhs = ctx.alloc_vreg(ctx.proc_regs[dest_vreg_id])
        tmp_vreg_rhs = ctx.alloc_vreg(ctx.proc_regs[dest_vreg_id])
        return (
            eval_expr(ctx, expr.lhs, tmp_vreg_lhs)
            + eval_expr(ctx, expr.rhs, tmp_vreg_rhs)
            + [ir.BinOp(dest_vreg_id, tmp_vreg_lhs, ir.BinaryOperator.from_ast_op(expr.operator), tmp_vreg_rhs)]
        )
    elif isinstance(expr, ast_mod.ProcedureCall):
        # TODO: set leaf!
        pass
    elif isinstance(expr, ast_mod.PointerIndex):
        ret = []

        var_found = find_variable(ctx, expr.var)
        match var_found["type"]:
            case "var":
                tmp_vreg_ptr = var_found["val"]["regid"]
            case "arg":
                tmp_vreg_ptr = ctx.alloc_vreg(var_found["val"]["type"])
                ret.append(ir.GetArgVal(tmp_vreg_ptr, expr.var))
            case "global":
                tmp_vreg_ptr = ctx.alloc_vreg(ir.DatatypePointer(var_found["val"]["type"]))
                ret.append(ir.GetGlobalPtr(tmp_vreg_ptr, expr.var))

        tmp_vreg_idx = ctx.alloc_vreg(ctx.datatypes["USIZE"])
        ret += eval_expr(ctx, expr.index_exp, tmp_vreg_idx)
        ret.append(ir.GetPtrReg(dest_vreg_id, tmp_vreg_ptr, tmp_vreg_idx, ctx.proc_regs[tmp_vreg_ptr].to))
        return ret

    raise NotImplementedError(f"unknown expr {expr}")
