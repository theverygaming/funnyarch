import sys
import ast
from dataclasses import dataclass
from random import random
import ir.ir as ir

def _assertion(value, error):
    if not value:
        raise Exception("Assertion failed: " + error)


def _assert_instance(o, c, errmsg):
    if not isinstance(o, c):
        print("error message: " + errmsg)
        raise Exception(f"{o} is not an instance if {c}")


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

def _gen_expr(ctx, result, op):
    if isinstance(op, ast.Constant):
        if isinstance(op.value, int):
            return [ ir.SetRegImm(result, op.value) ]
        if isinstance(op.value, str):
            ctx._global_counter += 1
            name = f"__compiler_global_{ctx._global_counter}_{int(random()*1000000000)}" # FIXME: this definitely isn't a great solution lol, we need non-exported globals
            ctx.globalvars[name] = [op.value]
            return [ ir.SetRegGlobalPtr(result, name) ]
        else:
            _assertion(False, "unsupported constant type")
    if isinstance(op, ast.Name): # variable copy
        _assertion(op.id in ctx.func_locals, f"undefined variable {op.id}")
        return [ ir.CopyReg(ctx.func_locals[op.id], result) ]
    if isinstance(op, ast.Call):
        return _gen_fn_call(ctx, op, result)
    if isinstance(op, ast.Subscript):
        _assertion(op.value.id in ctx.func_locals, f"undefined variable {op.value.id}")
        regn_src = ctx.func_locals[op.value.id]
        regn_offset = ctx.alloc_vreg()
        return _gen_expr(ctx, regn_offset, op.slice) + [ ir.ReadPointerReg(regn_src, result, regn_offset) ]
    _assert_instance(op, ast.BinOp, f"unsupported expr {ast.dump(op)}")
    ops = [] # tuple[list[ir], int[vregn]]
    for x in [op.left, op.right]:
        if isinstance(x, ast.Name):
            _assertion(x.id in ctx.func_locals, f"undefined variable {x.id}")
            ops.append(([], ctx.func_locals[x.id]))
            continue
        outn = ctx.alloc_vreg()
        ops.append((_gen_expr(ctx, outn, x), outn))
    return ops[0][0] + ops[1][0] + [ ir.ThreeAddressInstr(result, ops[0][1], ops[1][1], ir.astOp2IrOp(op.op)) ]

def _gen_fn_call(ctx, op, return_regn = None):
    _assertion(len(op.keywords) == 0, "no keyword arguments supported")
    _assert_instance(op.func, ast.Name, "weird function call")
    # builtins
    if op.func.id == "ord":
        _assertion(
            return_regn is not None
            and len(op.args) == 1
            and isinstance(op.args[0], ast.Constant)
            and isinstance(op.args[0].value, str)
            , "ord builtin used incorrectly"
        )
        return [ ir.SetRegImm(return_regn, ord(op.args[0].value)) ]
    ctx.func_is_leaf = False
    argRegs = []
    argRegIr = []
    for arg in op.args:
        reg = ctx.alloc_vreg()
        argRegs.append(reg)
        argRegIr += _gen_expr(ctx, reg, arg)
    if op.func.id in ctx.func_locals:
        n = ctx.func_locals[op.func.id]
    else:
        n = ctx.alloc_vreg()
        argRegIr.append(ir.SetRegGlobalPtr(n, op.func.id))
    return argRegIr + [ir.FuncCall(n, argRegs, return_regn)]

def gen_ast_node(ctx, node, depth=0):
    def print_d(s):
        print(f"{' ' * (depth*4)}{s}")

    print_d(f"irgen: {node}")

    for c, fn in _parsers:
        if isinstance(node, c):
            return fn(None, node)

    if isinstance(node, ast.Assign):
        print_d(f"assignment {ast.dump(node)}")
        _assertion(len(node.targets) == 1, "only one assignment target supported")
        target = node.targets[0]
        _assertion(isinstance(target, ast.Name) or isinstance(target, ast.Subscript), "can only assign to names or subscripts")
        _assert_instance(target.ctx, ast.Store, "can only store assign")
        if depth == 0:  # TODO: better way to check depth
            _assert_instance(target, ast.Name, "invalid global assignment")
            _assertion(isinstance(node.value, ast.Constant) or isinstance(node.value, ast.List), "can only assign constant or arrays of constants to globals")
            _assertion(target.id not in ctx.globalvars, "global variable already defined")
            if isinstance(node.value, ast.List):
                for el in node.value.elts:
                    _assert_instance(
                        el, ast.Constant, "can only assign constant to globals"
                    )
                ctx.globalvars[target.id] = [x.value for x in node.value.elts]
            else:
                ctx.globalvars[target.id] = [node.value.value]
        else:
            if isinstance(target, ast.Subscript):
                _assertion(target.value.id in ctx.func_locals, f"undefined variable {target.value.id}")
                regn_ptr = ctx.func_locals[target.value.id]
                regn_offset = ctx.alloc_vreg()
                regn_src = ctx.alloc_vreg()
                return _gen_expr(ctx, regn_src, node.value) + _gen_expr(ctx, regn_offset, target.slice) + [ ir.WritePointerReg(regn_ptr, regn_offset, regn_src) ]
            else:
                if target.id in ctx.func_locals:
                    n = ctx.func_locals[target.id]
                else:
                    n = ctx.alloc_vreg()
                    ctx.func_locals[target.id] = n
                return _gen_expr(ctx, n, node.value)
        return []

    if isinstance(node, ast.If):
        print_d(f"if stmt {ast.dump(node)}")
        _assert_instance(node.test, ast.Compare, "unsupported if statement")
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
            _assertion(len(node.test.ops) == 1, "unsupported if statement")
            _assertion(len(node.test.comparators) == 1, "unsupported if statement")
            cmpr1 = ctx.alloc_vreg()
            cmpir1 = _gen_expr(ctx, cmpr1, node.test.left)
            cmpr2 = ctx.alloc_vreg()
            cmpir2 = _gen_expr(ctx, cmpr2, node.test.comparators[0])

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
        _assert_instance(node.test, ast.Compare, "unsupported while loop")
        _assertion(len(node.orelse) == 0, "unsupported while loop")

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

        _assertion(len(node.test.ops) == 1, "unsupported while loop")
        _assertion(len(node.test.comparators) == 1, "unsupported while loop")
        cmpr1 = ctx.alloc_vreg()
        cmpir1 = _gen_expr(ctx, cmpr1, node.test.left)
        cmpr2 = ctx.alloc_vreg()
        cmpir2 = _gen_expr(ctx, cmpr2, node.test.comparators[0])
    

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
            _assertion(var not in ctx.func_locals, f"cannot use global {var} since it is already defined as a local")
            n = ctx.alloc_vreg()
            ctx.func_locals[var] = n
            body.append(ir.SetRegGlobalPtr(n, var))
        return body
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        print_d(f'expr {ast.dump(node.value)}')
        return _gen_fn_call(ctx, node.value)

    if isinstance(node, ast.Return):
        _assertion(depth > 0, "cannot return outside function")
        n = ctx.alloc_vreg()
        return _gen_expr(ctx, n, node.value) + [ir.FuncReturnReg(n)]

    if isinstance(node, ast.Break):
        _assertion(ctx.closestLoopEscapeLabel is not None, "invalid break")
        return [ir.JumpLocalLabel(ctx.closestLoopEscapeLabel)]

    if isinstance(node, ast.Continue):
        _assertion(ctx.closestLoopContinueLabel is not None, "invalid continue")
        return [ir.JumpLocalLabel(ctx.closestLoopContinueLabel)]
    
    if isinstance(node, ast.Pass):
        return []

    if (
        isinstance(node, ast.FunctionDef) and depth == 0
    ):  # TODO: better way to check depth
        print_d(f'function definition "{node.name}" args: {ast.dump(node.args, indent=1)}')
        _assertion(
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
            _assertion(arg.arg not in ctx.func_locals, "double argument")
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

    _assertion(False, f"cannot generate IR for AST node {ast.dump(node)}")


def gen_global_vars(ctx):
    irl = []
    for k, v in ctx.globalvars.items():
        irl.append(ir.GlobalVarDef(k, v))
    return irl
