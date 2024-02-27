import ast
import ir.ir as ir
import ir.lib as irlib
import ir.irgen as irgen


@irgen.reg_ast_node_parser(ast.Pass)
def parse_pass(_ctx, _node):
    return (True, [])


@irgen.reg_ast_node_parser(ast.Return)
def parse_return(ctx, node):
    irlib.assertion(ctx.depth > 0, "cannot return outside function")
    n = ctx.alloc_vreg()
    return (True, irlib.gen_expr(ctx, n, node.value) + [ir.FuncReturnReg(n)])


@irgen.reg_ast_node_parser(ast.Break)
def parse_break(ctx, node):
    irlib.assertion(ctx.closestLoopEscapeLabel is not None, "invalid break")
    return (True, [ir.JumpLocalLabel(ctx.closestLoopEscapeLabel)])


@irgen.reg_ast_node_parser(ast.Continue)
def parse_continue(ctx, node):
    irlib.assertion(ctx.closestLoopContinueLabel is not None, "invalid continue")
    return (True, [ir.JumpLocalLabel(ctx.closestLoopContinueLabel)])


@irgen.reg_ast_node_parser(ast.Expr)
def parse_expr(ctx, node):
    if not isinstance(node.value, ast.Call):
        return (False, None)
    return (True, irlib.gen_call(ctx, node.value))


@irgen.reg_ast_node_parser(ast.Global)
def parse_global(ctx, node):
    body = []
    for var in node.names:
        irlib.assertion(
            var not in ctx.func_locals,
            f"cannot use global {var} since it is already defined as a local",
        )
        n = ctx.alloc_vreg()
        ctx.func_locals[var] = n
        body.append(ir.SetRegGlobalPtr(n, var))
    return (True, body)
