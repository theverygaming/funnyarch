from idfkanymore.parse import ast_mod
from .. import ir
from .. import lib as irlib
from .. import irgen as irgen
from . import expr

def gen_call(ctx, fn_name, arg_expr_list, retval_vreg=None):
    ctx.proc_is_leaf = False
    # FIXME: verify fn name??
    ret = []
    arg_vregs = []
    for arg_expr in arg_expr_list:
        # FIXME: args types???? Check fn signature??? # BUG:
        tmp_arg_vreg = ctx.alloc_vreg(ctx.datatypes["REGISTER"])
        arg_vregs.append(tmp_arg_vreg)
        ret += expr.eval_expr(ctx, arg_expr, tmp_arg_vreg)
    tmp_fnptr_vreg = ctx.alloc_vreg(ctx.datatypes["REGISTER"])
    ret += [
        ir.FuncCall(None, fn_name, arg_vregs, retval_vreg),
    ]
    return ret


@irgen.reg_ast_node_parser((ast_mod.ProcedureDecl,))
def parse_procedure_decl(ctx, node, bubble):
    return []

@irgen.reg_ast_node_parser((ast_mod.ProcedureDef,))
def parse_procedure_def(ctx, node, bubble):
    args = [(arg.name, ctx.lookup_type(arg.type_)) for arg in node.prototype.args]
    localvars = [(var.name, ctx.lookup_type(var.type_)) for var in node.vars_]

    ctx.proc_locals = {}
    ctx.proc_is_leaf = True
    ctx.proc_vreg_counter = -1
    ctx.proc_regs = {}
    ctx.proc_label_counter = -1
    ctx.proc_closest_loop_escape_label = None
    ctx.proc_closest_loop_continue_label = None
    ctx.proc_return_type = ctx.lookup_type(node.prototype.return_type)

    for name, t in args:
        ctx.proc_locals[name] = {
            "kind": "arg",
            "type": t,
        }
    for name, t in localvars:
        ctx.proc_locals[name] = {
            "kind": "var",
            "type": t,
            "regid": ctx.alloc_vreg(t),
        }

    body = []
    for n in node.block.statements:
        body += bubble(n)

    return [
        ir.Function(
            node.prototype.name,
            ctx.proc_is_leaf,
            args,
            ctx.proc_return_type,
            ctx.proc_regs,
            body,
            True,
        )
    ]

@irgen.reg_ast_node_parser((ast_mod.ProcedureCall,), end_only=True)
def parse_procedure_call(ctx, node, bubble):
    return gen_call(ctx, node.name, node.args)
