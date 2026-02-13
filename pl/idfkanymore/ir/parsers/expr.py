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


def read_variable(ctx, name, dst_vreg_id: int | None = None):
    """
    read a variable into a register, if dst_vreg_id is not set, a register to be referenced will be returned (setting that register may be UB!).

    when you set dst_vreg_id you may ignore the returned value register and cleanup ircode, nothing will ever be allocated if you provide a vreg id

    return:
    (ircode, value register, cleanup ircode)
    """
    var_found = find_variable(ctx, name)
    match var_found["type"]:
        case "var":
            if dst_vreg_id is None:
                return ([], var_found["val"]["regid"], [])
            return ([ir.CopyReg(var_found["val"]["regid"], dst_vreg_id)], None, [])
        case "arg":
            if dst_vreg_id is None:
                tmp_vreg = ctx.alloc_vreg(var_found["val"]["type"])
                return ([ir.StartUseRegs([tmp_vreg]), ir.GetArgVal(tmp_vreg, name)], tmp_vreg, [ir.EndUseRegs([tmp_vreg])])
            return ([ir.GetArgVal(dst_vreg_id, name)], None, [])
        case "global":
            if dst_vreg_id is None:
                reg_val_dst = ctx.alloc_vreg(var_found["val"]["type"])
            else:
                reg_val_dst = dst_vreg_id
            tmp_vreg_ptr = ctx.alloc_vreg(ir.DatatypePointer(var_found["val"]["type"]))
            tmp_vreg_idx = ctx.alloc_vreg(ctx.datatypes["USIZE"])
            return (
                [
                    ir.StartUseRegs([tmp_vreg_ptr]),
                    ir.GetGlobalPtr(tmp_vreg_ptr, name),
                    ir.StartUseRegs([tmp_vreg_idx]),
                    ir.SetRegImm(tmp_vreg_idx, 0),
                ]
                + ([ir.StartUseRegs([reg_val_dst])] if dst_vreg_id is None else [])
                + [
                    ir.GetPtrReg(reg_val_dst, tmp_vreg_ptr, tmp_vreg_idx, var_found["val"]["type"]),
                    ir.EndUseRegs([tmp_vreg_ptr, tmp_vreg_idx]),
                ],
                reg_val_dst if dst_vreg_id is None else None,
                [ir.EndUseRegs([reg_val_dst])] if dst_vreg_id is None else [],
            )
        case _:
            raise Exception(f"read_variable: unsupported variable type {var_found['type']}")


def write_variable_ref(ctx, name):
    """
    set a variable value. When possible will be done without an extra copy operation

    return: (function(call before set): returns ircode and vreg ID to write, function (call after set): returns ircode)
    """
    var_found = find_variable(ctx, name)
    match var_found["type"]:
        case "var":
            def fn1():
                return ([], var_found["val"]["regid"])
            def fn2():
                return []
            return (fn1, fn2)
        case "global":
            val_vreg = ctx.alloc_vreg(var_found["val"]["type"])
            tmp_vreg_ptr = ctx.alloc_vreg(ir.DatatypePointer(var_found["val"]["type"]))
            tmp_vreg_idx = ctx.alloc_vreg(ctx.datatypes["USIZE"])
            def fn1():
                return ([ir.StartUseRegs([val_vreg])], val_vreg)
            def fn2():
                return [
                    ir.StartUseRegs([tmp_vreg_ptr]),
                    ir.GetGlobalPtr(tmp_vreg_ptr, name),
                    ir.StartUseRegs([tmp_vreg_idx]),
                    ir.SetRegImm(tmp_vreg_idx, 0),
                    ir.SetPtrReg(tmp_vreg_ptr, tmp_vreg_idx, val_vreg, var_found["val"]["type"]),
                    ir.EndUseRegs([val_vreg, tmp_vreg_ptr, tmp_vreg_idx]),
                ]
            return (fn1, fn2)
        case _:
            raise Exception(f"write_variable: unsupported variable type {var_found['type']}")


def write_variable(ctx, name, src_vreg: int):
    """
    set a variable value to the value of a register.

    return: ircode
    """
    fn1, fn2 = write_variable_ref(ctx, name)

    out = []

    ircode, vreg_id = fn1()
    out += ircode
    out.append(ir.CopyReg(src_vreg, vreg_id))
    out += fn2()

    return out


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
        out, _, _ = read_variable(ctx, expr.name, dest_vreg_id)
        return out
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

        readvar_code, vreg_ptr, code_vregs_dealloc = read_variable(ctx, expr.var)
        ret += readvar_code

        tmp_vreg_idx = ctx.alloc_vreg(ctx.datatypes["USIZE"])
        ret.append(ir.StartUseRegs([tmp_vreg_idx]))
        ret += eval_expr(ctx, expr.index_exp, tmp_vreg_idx)
        ret.append(ir.GetPtrReg(dest_vreg_id, vreg_ptr, tmp_vreg_idx, ctx.proc_regs[vreg_ptr].to))
        ret.append(ir.EndUseRegs([tmp_vreg_idx]))

        ret += code_vregs_dealloc
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
