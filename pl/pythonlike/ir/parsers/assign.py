import ast
import ir.ir as ir
import ir.lib as irlib
import ir.irgen as irgen


@irgen.reg_ast_node_parser(ast.Assign)
def parse_assign(ctx, node):
    irlib.assertion(len(node.targets) == 1, "only one assignment target supported")
    target = node.targets[0]
    irlib.assertion(
        isinstance(target, ast.Name) or isinstance(target, ast.Subscript),
        "can only assign to names or subscripts",
    )
    irlib.assert_instance(target.ctx, ast.Store, "can only store assign")
    if ctx.depth == 0:  # TODO: better way to check depth
        irlib.assert_instance(target, ast.Name, "invalid global assignment")
        irlib.assertion(
            isinstance(node.value, ast.Constant) or isinstance(node.value, ast.List),
            "can only assign constant or arrays of constants to globals",
        )
        irlib.assertion(
            target.id not in ctx.globalvars, "global variable already defined"
        )
        if isinstance(node.value, ast.List):
            for el in node.value.elts:
                irlib.assert_instance(
                    el, ast.Constant, "can only assign constant to globals"
                )
            ctx.globalvars[target.id] = [x.value for x in node.value.elts]
        else:
            ctx.globalvars[target.id] = [node.value.value]
    else:
        if isinstance(target, ast.Subscript):
            irlib.assertion(
                target.value.id in ctx.func_locals,
                f"undefined variable {target.value.id}",
            )
            regn_ptr = ctx.func_locals[target.value.id]
            regn_offset = ctx.alloc_vreg()
            regn_src = ctx.alloc_vreg()
            return (
                True,
                irlib.gen_expr(ctx, regn_src, node.value)
                + irlib.gen_expr(ctx, regn_offset, target.slice)
                + [ir.WritePointerReg(regn_ptr, regn_offset, regn_src)],
            )
        else:
            if target.id in ctx.func_locals:
                n = ctx.func_locals[target.id]
            else:
                n = ctx.alloc_vreg()
                ctx.func_locals[target.id] = n
            return (True, irlib.gen_expr(ctx, n, node.value))
    return (True, [])
