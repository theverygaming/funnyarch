from idfkanymore.parse import ast_mod
from .. import ir
from .. import lib as irlib
from .. import irgen as irgen
from . import procedure

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
    if isinstance(expr, ast_mod.Constant):
        if isinstance(expr.value, int):
            return [ir.SetRegImm(dest_vreg_id, expr.value)]
        elif isinstance(expr.value, str):
            varname = f"__global_str_{abs(hash(expr.value))}"
            if varname not in ctx.globalvars:
                ctx.globalvars[varname] = {
                    "type": ir.DatatypeArray(ctx.datatypes["U8"], len(expr.value) + 1),
                    "value": [b for b in expr.value.encode("utf-8")] + [0],
                    "def": True,
                    "attributes": {},
                }
            return [ir.GetGlobalPtr(dest_vreg_id, varname)]
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
                    ir.StartUseRegs([tmp_vreg_ptr, tmp_vreg_idx]),
                    ir.GetGlobalPtr(tmp_vreg_ptr, expr.name),
                    ir.SetRegImm(tmp_vreg_idx, 0),
                    ir.GetPtrReg(dest_vreg_id, tmp_vreg_ptr, tmp_vreg_idx, var_found["val"]["type"]),
                    ir.EndUseRegs([tmp_vreg_ptr, tmp_vreg_idx]),
                ]
    elif isinstance(expr, ast_mod.Binop):
        tmp_vreg_lhs = ctx.alloc_vreg(ctx.proc_regs[dest_vreg_id])
        tmp_vreg_rhs = ctx.alloc_vreg(ctx.proc_regs[dest_vreg_id])
        return (
            [ir.StartUseRegs([tmp_vreg_lhs])]
            + eval_expr(ctx, expr.lhs, tmp_vreg_lhs)
            + [ir.StartUseRegs([tmp_vreg_rhs])]
            + eval_expr(ctx, expr.rhs, tmp_vreg_rhs)
            + [
                ir.BinOp(dest_vreg_id, tmp_vreg_lhs, ir.BinaryOperator.from_ast_op(expr.operator), tmp_vreg_rhs),
                ir.EndUseRegs([tmp_vreg_lhs, tmp_vreg_rhs]),
            ]
        )
    elif isinstance(expr, ast_mod.ProcedureCall):
        return procedure.gen_call(ctx, expr.name, expr.args, dest_vreg_id)
    elif isinstance(expr, ast_mod.PointerIndex):
        ret = []

        var_found = find_variable(ctx, expr.var)
        match var_found["type"]:
            case "var":
                vreg_ptr = var_found["val"]["regid"]
            case "arg":
                vreg_ptr = ctx.alloc_vreg(var_found["val"]["type"])
                ret.append(ir.StartUseRegs([vreg_ptr]))
                ret.append(ir.GetArgVal(vreg_ptr, expr.var))
            case "global":
                tmp_vreg_global_ptr = ctx.alloc_vreg(ir.DatatypePointer(var_found["val"]["type"]))
                tmp_vreg_idx_global = ctx.alloc_vreg(ctx.datatypes["USIZE"])
                vreg_ptr = ctx.alloc_vreg(var_found["val"]["type"])
                ret += [
                    ir.StartUseRegs([tmp_vreg_global_ptr]),
                    ir.GetGlobalPtr(tmp_vreg_global_ptr, expr.var),
                    ir.StartUseRegs([vreg_ptr]),
                    ir.StartUseRegs([tmp_vreg_idx_global]),
                    ir.SetRegImm(tmp_vreg_idx_global, 0),
                    ir.GetPtrReg(vreg_ptr, tmp_vreg_global_ptr, tmp_vreg_idx_global, ctx.proc_regs[tmp_vreg_global_ptr]),
                    ir.EndUseRegs([tmp_vreg_global_ptr, tmp_vreg_idx_global]),
                ]

        tmp_vreg_idx = ctx.alloc_vreg(ctx.datatypes["USIZE"])
        ret.append(ir.StartUseRegs([tmp_vreg_idx]))
        ret += eval_expr(ctx, expr.index_exp, tmp_vreg_idx)
        ret.append(ir.GetPtrReg(dest_vreg_id, vreg_ptr, tmp_vreg_idx, ctx.proc_regs[vreg_ptr].to))
        ret.append(ir.EndUseRegs([tmp_vreg_idx]))
        match var_found["type"]:
            case "arg":
                ret.append(ir.EndUseRegs([vreg_ptr]))
            case "global":
                ret.append(ir.EndUseRegs([vreg_ptr]))
        return ret
    elif isinstance(expr, ast_mod.Comparison):
        tmp_vreg_lhs = ctx.alloc_vreg(ctx.proc_regs[dest_vreg_id])
        tmp_vreg_rhs = ctx.alloc_vreg(ctx.proc_regs[dest_vreg_id])
        return (
            [ir.StartUseRegs([tmp_vreg_lhs])]
            + eval_expr(ctx, expr.lhs, tmp_vreg_lhs)
            + [ir.StartUseRegs([tmp_vreg_rhs])]
            + eval_expr(ctx, expr.rhs, tmp_vreg_rhs)
            + [ir.Compare(dest_vreg_id, tmp_vreg_lhs, ir.CompareOperator.from_ast_op(expr.operator), tmp_vreg_rhs)]
            + [ir.EndUseRegs([tmp_vreg_lhs, tmp_vreg_rhs])]
        )
    elif isinstance(expr, ast_mod.Unaryop):
        tmp_vreg = ctx.alloc_vreg(ctx.proc_regs[dest_vreg_id])
        return (
            [ir.StartUseRegs([tmp_vreg])]
            + eval_expr(ctx, expr.expr, tmp_vreg)
            + [ir.UnaryOp(dest_vreg_id, ir.UnaryOperator.from_ast_op(expr.operator), tmp_vreg)]
            + [ir.EndUseRegs([tmp_vreg])]
        )

    raise NotImplementedError(f"unknown expr {expr}")
