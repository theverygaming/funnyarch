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
        var_found = expr.find_variable(ctx, var_name)
        dst = var_found["val"]
        irlib.assertion(var_found["type"] in ["var", "global"], "can only assign to variables")
        is_local = var_found["type"] == "var"

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

@irgen.reg_ast_node_parser((ast_mod.Return,), end_only=True)
def parse_return(ctx, node, bubble):
    ret = []
    dst_vreg = ctx.alloc_vreg(ctx.proc_return_type)
    ret += expr.eval_expr(ctx, node.expr, dst_vreg)
    ret.append(ir.FuncReturn(dst_vreg))
    return ret

@irgen.reg_ast_node_parser((ast_mod.While,), end_only=True)
def parse_while(ctx, node, bubble):
    lbl_start = ctx.alloc_label()
    lbl_end = ctx.alloc_label()

    prev_lbl_esc = ctx.proc_closest_loop_escape_label
    prev_lbl_cont = ctx.proc_closest_loop_continue_label
    ctx.proc_closest_loop_escape_label = lbl_end
    ctx.proc_closest_loop_continue_label = lbl_start
    body = []
    for n in node.block.statements:
        body += bubble(n)
    ctx.proc_closest_loop_escape_label = prev_lbl_esc
    ctx.proc_closest_loop_continue_label = prev_lbl_cont

    cond_vreg = ctx.alloc_vreg(ctx.datatypes["REGISTER"])

    return ([
        ir.LocalLabel(lbl_start),
    ] + expr.eval_expr(ctx, node.cond, cond_vreg) + [
        ir.JumpLocalLabelCondFalsy(lbl_end, cond_vreg),
    ] + body + [
        ir.LocalLabel(lbl_end),
    ])
