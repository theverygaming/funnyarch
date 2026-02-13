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
        fn1, fn2 = expr.write_variable_ref(ctx, var_name)
        ircode, vreg_id = fn1()
        ret += ircode
        ret += expr.eval_expr(ctx, node.value, vreg_id)
        ret += fn2()
    elif isinstance(node.to, ast_mod.PointerIndex):
        readvar_code, ptr_vreg, code_vregs_dealloc = expr.read_variable(ctx, node.to.var)

        val_vreg = ctx.alloc_vreg(ctx.proc_regs[ptr_vreg].to)
        ret.append(ir.StartUseRegs([val_vreg]))
        ret += expr.eval_expr(ctx, node.value, val_vreg)
        idx_vreg = ctx.alloc_vreg(ctx.datatypes["USIZE"])
        ret.append(ir.StartUseRegs([idx_vreg]))
        ret += expr.eval_expr(ctx, node.to.index_exp, idx_vreg)

        ret += readvar_code

        ret.append(ir.SetPtrReg(ptr_vreg, idx_vreg, val_vreg, ctx.proc_regs[ptr_vreg].to))
        ret.append(ir.EndUseRegs([val_vreg, idx_vreg]))

        ret += code_vregs_dealloc
    else:
        raise Exception("qwhar??")
    return ret

@irgen.reg_ast_node_parser((ast_mod.Return,), end_only=True)
def parse_return(ctx, node, bubble):
    ret = []
    dst_vreg = ctx.alloc_vreg(ctx.proc_return_type)
    ret.append(ir.StartUseRegs([dst_vreg]))
    ret += expr.eval_expr(ctx, node.expr, dst_vreg)
    ret.append(ir.FuncReturn(dst_vreg))
    ret.append(ir.EndUseRegs([dst_vreg]))
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
        ir.StartUseRegs([cond_vreg]),
    ] + expr.eval_expr(ctx, node.cond, cond_vreg) + [
        ir.JumpLocalLabelCondFalsy(lbl_end, cond_vreg),
        ir.EndUseRegs([cond_vreg]),
    ] + body + [
        ir.JumpLocalLabel(lbl_start),
        ir.LocalLabel(lbl_end),
    ])

@irgen.reg_ast_node_parser((ast_mod.If,), end_only=True)
def parse_if(ctx, node, bubble):
    def _gen_simple_if(cond, body, lbl_else, lbl_after_then):
        ret = []

        if cond is not None:
            cond_vreg = ctx.alloc_vreg(ctx.datatypes["REGISTER"])
            ret.append(ir.StartUseRegs([cond_vreg]))
            ret += expr.eval_expr(ctx, cond, cond_vreg)
            ret.append(ir.JumpLocalLabelCondFalsy(lbl_else, cond_vreg))
            ret.append(ir.EndUseRegs([cond_vreg]))

        for n in body:
            ret += bubble(n)
        
        if lbl_after_then is not None:
            ret.append(ir.JumpLocalLabel(lbl_after_then))

        return ret

    ret = []

    # prepare
    if_chain = []
    if_chain.append([node.cond, node.then])
    if_chain += map(list, node.elsif)
    if node.else_ is not None:
        if_chain.append([None, node.else_])
    lbl_if_end = ctx.alloc_label()

    # generate a label for each branch that isn't the first, and add labels for the next
    for i in reversed(range(len(if_chain))):
        lbl_self = None
        if i != 0:
            lbl_self = ctx.alloc_label()
        if_chain[i].append(lbl_self)

    # add else labels
    for i in range(len(if_chain)):
        lbl_else = None
        # everything other than last one has a else label
        if i != len(if_chain) - 1:
            lbl_else = if_chain[i+1][2]
        # the last one has the end label as else
        else:
            lbl_else = lbl_if_end
        if_chain[i].append(lbl_else)

    # generate code
    for i, (cond, body, lbl_self, lbl_else) in enumerate(if_chain):
        if lbl_self is not None:
            ret.append(ir.LocalLabel(lbl_self))
        # everything other than last one gets a jump to end
        lbl_after_then = lbl_if_end if  i != len(if_chain) - 1 else None
        ret += _gen_simple_if(cond, body.statements, lbl_else, lbl_after_then)
    ret.append(ir.LocalLabel(lbl_if_end))

    return ret
