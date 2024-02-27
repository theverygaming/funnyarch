import ast
import ir.ir as ir
import ir.lib as irlib
import ir.irgen as irgen


@irgen.reg_ast_node_parser(ast.While)
def parse_loop_while(ctx, node):
    irlib.assert_instance(node.test, ast.Compare, "unsupported while loop")
    irlib.assertion(len(node.orelse) == 0, "unsupported while loop")

    lblLoopStart = f"L{ctx.alloc_label()}"
    lblLoopBody = f"L{ctx.alloc_label()}"
    lblLoopEsc = f"L{ctx.alloc_label()}"

    _prev_closest_esc = ctx.closestLoopEscapeLabel
    _prev_closest_cont = ctx.closestLoopContinueLabel

    ctx.closestLoopEscapeLabel = lblLoopEsc
    ctx.closestLoopContinueLabel = lblLoopStart

    ctx.depth += 1
    body = []
    for n in node.body:
        body += irgen.gen_ast_node(ctx, n)
    ctx.depth -= 1

    ctx.closestLoopEscapeLabel = _prev_closest_esc
    ctx.closestLoopContinueLabel = _prev_closest_cont

    irlib.assertion(len(node.test.ops) == 1, "unsupported while loop")
    irlib.assertion(len(node.test.comparators) == 1, "unsupported while loop")
    cmpr1 = ctx.alloc_vreg()
    cmpir1 = irlib.gen_expr(ctx, cmpr1, node.test.left)
    cmpr2 = ctx.alloc_vreg()
    cmpir2 = irlib.gen_expr(ctx, cmpr2, node.test.comparators[0])

    return (
        True,
        (
            [ir.LocalLabel(lblLoopStart)]
            + cmpir1
            + cmpir2
            + [
                ir.Compare(
                    cmpr1,
                    cmpr2,
                    ir.astCmpOp2IrCmpOp(node.test.ops[0]),
                    lblLoopBody,
                    lblLoopEsc,
                )
            ]
            + [ir.LocalLabel(lblLoopBody)]
            + body
            + [ir.JumpLocalLabel(lblLoopStart)]
            + [ir.LocalLabel(lblLoopEsc)]
            # + orelse
        ),
    )
