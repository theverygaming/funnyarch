import sys
import ast
from dataclasses import dataclass
import ir.lib as irlib
import ir.ir as ir


@dataclass
class IrGenContext():
    globalvars = {}
    func_locals = None
    func_is_leaf = False
    _vreg_counter = -1
    _label_counter = -1
    _global_counter = -1
    closestLoopEscapeLabel = None
    closestLoopContinueLabel = None
    
    def alloc_vreg(self):
        self._vreg_counter += 1
        return self._vreg_counter
    
    def alloc_label(self):
        self._label_counter += 1
        return self._label_counter

_parsers = []

def reg_ast_node_parser(c):
    def fn2(fn):
        _parsers.append((c, fn))
        return fn
    return fn2

def gen_ast_node(ctx, node, depth=0):
    def print_d(s):
        print(f"{' ' * (depth*4)}{s}")

    print_d(f"irgen: {node}")

    for c, fn in _parsers:
        if isinstance(node, c):
            success, data = fn(ctx, node)
            if success:
                return data

    if isinstance(node, ast.Assign):
        print_d(f"assignment {ast.dump(node)}")
        irlib.assertion(len(node.targets) == 1, "only one assignment target supported")
        target = node.targets[0]
        irlib.assertion(isinstance(target, ast.Name) or isinstance(target, ast.Subscript), "can only assign to names or subscripts")
        irlib.assert_instance(target.ctx, ast.Store, "can only store assign")
        if depth == 0:  # TODO: better way to check depth
            irlib.assert_instance(target, ast.Name, "invalid global assignment")
            irlib.assertion(isinstance(node.value, ast.Constant) or isinstance(node.value, ast.List), "can only assign constant or arrays of constants to globals")
            irlib.assertion(target.id not in ctx.globalvars, "global variable already defined")
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
                irlib.assertion(target.value.id in ctx.func_locals, f"undefined variable {target.value.id}")
                regn_ptr = ctx.func_locals[target.value.id]
                regn_offset = ctx.alloc_vreg()
                regn_src = ctx.alloc_vreg()
                return irlib.gen_expr(ctx, regn_src, node.value) + irlib.gen_expr(ctx, regn_offset, target.slice) + [ ir.WritePointerReg(regn_ptr, regn_offset, regn_src) ]
            else:
                if target.id in ctx.func_locals:
                    n = ctx.func_locals[target.id]
                else:
                    n = ctx.alloc_vreg()
                    ctx.func_locals[target.id] = n
                return irlib.gen_expr(ctx, n, node.value)
        return []

    if isinstance(node, ast.If):
        print_d(f"if stmt {ast.dump(node)}")
        irlib.assert_instance(node.test, ast.Compare, "unsupported if statement")
        lblIfTrue = f"L{ctx.alloc_label()}"
        lblIfFalse = f"L{ctx.alloc_label()}"
        lblIfEnd = f"L{ctx.alloc_label()}"
        
        body = []
        for n in node.body:
            body += gen_ast_node(ctx, n, depth + 1)
        orelse = []
        for n in node.orelse:
            orelse += gen_ast_node(ctx, n, depth + 1)

        if isinstance(node.test, ast.Compare):
            irlib.assertion(len(node.test.ops) == 1, "unsupported if statement")
            irlib.assertion(len(node.test.comparators) == 1, "unsupported if statement")
            cmpr1 = ctx.alloc_vreg()
            cmpir1 = irlib.gen_expr(ctx, cmpr1, node.test.left)
            cmpr2 = ctx.alloc_vreg()
            cmpir2 = irlib.gen_expr(ctx, cmpr2, node.test.comparators[0])

            return (
                cmpir1
                + cmpir2
                + [ir.Compare(cmpr1, cmpr2, ir.astCmpOp2IrCmpOp(node.test.ops[0]), lblIfTrue, lblIfFalse)]
                + [ir.LocalLabel(lblIfTrue)]
                + body
                + [ir.JumpLocalLabel(lblIfEnd)]
                + [ir.LocalLabel(lblIfFalse)]
                + orelse
                + [ir.LocalLabel(lblIfEnd)]
            )
    
    if isinstance(node, ast.While):
        print_d(f"while loop {ast.dump(node)}")
        irlib.assert_instance(node.test, ast.Compare, "unsupported while loop")
        irlib.assertion(len(node.orelse) == 0, "unsupported while loop")

        lblLoopStart = f"L{ctx.alloc_label()}"
        lblLoopBody = f"L{ctx.alloc_label()}"
        lblLoopEsc = f"L{ctx.alloc_label()}"

        _prev_closest_esc = ctx.closestLoopEscapeLabel
        _prev_closest_cont = ctx.closestLoopContinueLabel

        ctx.closestLoopEscapeLabel = lblLoopEsc
        ctx.closestLoopContinueLabel = lblLoopStart

        body = []
        for n in node.body:
            body += gen_ast_node(ctx, n, depth + 1)

        ctx.closestLoopEscapeLabel = _prev_closest_esc
        ctx.closestLoopContinueLabel = _prev_closest_cont

        irlib.assertion(len(node.test.ops) == 1, "unsupported while loop")
        irlib.assertion(len(node.test.comparators) == 1, "unsupported while loop")
        cmpr1 = ctx.alloc_vreg()
        cmpir1 = irlib.gen_expr(ctx, cmpr1, node.test.left)
        cmpr2 = ctx.alloc_vreg()
        cmpir2 = irlib.gen_expr(ctx, cmpr2, node.test.comparators[0])
    

        return (
            [ir.LocalLabel(lblLoopStart)]
            + cmpir1
            + cmpir2
            + [ir.Compare(cmpr1, cmpr2, ir.astCmpOp2IrCmpOp(node.test.ops[0]), lblLoopBody, lblLoopEsc)]
            + [ir.LocalLabel(lblLoopBody)]
            + body
            + [ir.JumpLocalLabel(lblLoopStart)]
            + [ir.LocalLabel(lblLoopEsc)]
            #+ orelse
        )
    
    if isinstance(node, ast.Global):
        body = []
        for var in node.names:
            irlib.assertion(var not in ctx.func_locals, f"cannot use global {var} since it is already defined as a local")
            n = ctx.alloc_vreg()
            ctx.func_locals[var] = n
            body.append(ir.SetRegGlobalPtr(n, var))
        return body
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        print_d(f'expr {ast.dump(node.value)}')
        return irlib.gen_call(ctx, node.value)

    if isinstance(node, ast.Return):
        irlib.assertion(depth > 0, "cannot return outside function")
        n = ctx.alloc_vreg()
        return irlib.gen_expr(ctx, n, node.value) + [ir.FuncReturnReg(n)]

    if (
        isinstance(node, ast.FunctionDef) and depth == 0
    ):  # TODO: better way to check depth
        print_d(f'function definition "{node.name}" args: {ast.dump(node.args, indent=1)}')
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
        for n in node.body:
            fbody += gen_ast_node(ctx, n, depth + 1)
        for deco in node.decorator_list:
            if isinstance(deco, ast.Name):
                if deco.id == "export":
                    func_export = True
        return [ir.Function(node.name, ctx.func_is_leaf, func_export, len(ctx.func_locals), len(node.args.args), fbody)]

    irlib.assertion(False, f"cannot generate IR for AST node {ast.dump(node)}")


def gen_global_vars(ctx):
    irl = []
    for k, v in ctx.globalvars.items():
        irl.append(ir.GlobalVarDef(k, v))
    return irl
