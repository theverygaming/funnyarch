from idfkanymore.parse import ast_mod
from .. import ir
from .. import lib as irlib
from .. import irgen as irgen

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

    return_type = ctx.lookup_type(node.prototype.return_type)

    body = []
    for n in node.block.statements:
        body += bubble(n)

    return [
        ir.Function(
            node.prototype.name,
            ctx.proc_is_leaf,
            args,
            return_type,
            ctx.proc_regs,
            body,
            True,
        )
    ]
