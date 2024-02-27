import ast
import ir.ir as ir
import ir.lib as irlib
import ir.irgen as irgen


@irgen.reg_ast_node_parser(ast.Pass)
def parse_pass(_ctx, node):
    return (True, [])


#@irgen.reg_ast_node_parser(ast.Return)
#def parse_return(_ctx, node):
#    irlib.assertion(depth > 0, "cannot return outside function")
#    n = ctx.alloc_vreg()
#    return (True, irlib.gen_expr(ctx, n, node.value) + [ir.FuncReturnReg(n)])


@irgen.reg_ast_node_parser(ast.Break)
def parse_break(ctx, node):
    irlib.assertion(ctx.closestLoopEscapeLabel is not None, "invalid break")
    return (True, [ir.JumpLocalLabel(ctx.closestLoopEscapeLabel)])


@irgen.reg_ast_node_parser(ast.Continue)
def parse_continue(ctx, node):
    irlib.assertion(ctx.closestLoopContinueLabel is not None, "invalid continue")
    return (True, [ir.JumpLocalLabel(ctx.closestLoopContinueLabel)])
