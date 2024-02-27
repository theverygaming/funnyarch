import ast
import ir.ir as ir
import ir.lib as irlib
import ir.irgen as irgen


@irgen.reg_ast_node_parser(ast.If)
def parse_if(ctx, node):
    irlib.assert_instance(node.test, ast.Compare, "unsupported if statement")
    lblIfTrue = f"L{ctx.alloc_label()}"
    lblIfFalse = f"L{ctx.alloc_label()}"
    lblIfEnd = f"L{ctx.alloc_label()}"

    body = []
    ctx.depth += 1
    for n in node.body:
        body += irgen.gen_ast_node(ctx, n)
    orelse = []
    for n in node.orelse:
        orelse += irgen.gen_ast_node(ctx, n)
    ctx.depth -= 1

    if isinstance(node.test, ast.Compare):
        irlib.assertion(len(node.test.ops) == 1, "unsupported if statement")
        irlib.assertion(len(node.test.comparators) == 1, "unsupported if statement")
        cmpr1 = ctx.alloc_vreg()
        cmpir1 = irlib.gen_expr(ctx, cmpr1, node.test.left)
        cmpr2 = ctx.alloc_vreg()
        cmpir2 = irlib.gen_expr(ctx, cmpr2, node.test.comparators[0])

        return (
            True,
            (
                cmpir1
                + cmpir2
                + [
                    ir.Compare(
                        cmpr1,
                        cmpr2,
                        ir.astCmpOp2IrCmpOp(node.test.ops[0]),
                        lblIfTrue,
                        lblIfFalse,
                    )
                ]
                + [ir.LocalLabel(lblIfTrue)]
                + body
                + [ir.JumpLocalLabel(lblIfEnd)]
                + [ir.LocalLabel(lblIfFalse)]
                + orelse
                + [ir.LocalLabel(lblIfEnd)]
            ),
        )
