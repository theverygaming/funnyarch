import ast
import ir.ir as ir
import ir.lib as irlib
import ir.irgen as irgen


@irgen.reg_ast_node_parser(ast.FunctionDef)
def parse_func_def(ctx, node):
    if ctx.depth != 0:
        return (False, None)
    irlib.assertion(
        len(node.args.posonlyargs) == 0
        and len(node.args.kwonlyargs) == 0
        and node.args.vararg is None
        and node.args.kwarg is None
        and len(node.args.kw_defaults) == 0
        and len(node.args.defaults) == 0,
        "only normal args supported",
    )
    ctx.func_locals = {}
    ctx.func_is_leaf = True
    ctx._label_counter = -1

    func_export = False
    fbody = []
    for argn, arg in enumerate(node.args.args):
        irlib.assertion(arg.arg not in ctx.func_locals, "double argument")
        n = ctx.alloc_vreg()
        ctx.func_locals[arg.arg] = n
        fbody.append(ir.SetRegFuncArg(n, argn))
    ctx.depth += 1
    for n in node.body:
        fbody += irgen.gen_ast_node(ctx, n)
    ctx.depth -= 1
    for deco in node.decorator_list:
        if isinstance(deco, ast.Name):
            if deco.id == "export":
                func_export = True
    return (
        True,
        [
            ir.Function(
                node.name,
                ctx.func_is_leaf,
                func_export,
                len(ctx.func_locals),
                len(node.args.args),
                fbody,
            )
        ],
    )
