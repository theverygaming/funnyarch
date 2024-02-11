import sys
import ast
import ir


def _assertion(value, error):
    if not value:
        raise Exception("Assertion failed: " + error)


def _assert_instance(o, c, errmsg):
    if not isinstance(o, c):
        print("error message: " + errmsg)
        raise Exception(f"{o} is not an instance if {c}")


_globalvars = {}

_func_locals = None
_func_is_leaf = False

_vreg_counter = -1
_label_counter = -1
_global_counter = -1

_closestLoopEscapeLabel = None
_closestLoopContinueLabel = None


def _alloc_vreg():
    global _vreg_counter
    _vreg_counter += 1
    return _vreg_counter

def _gen_expr(result, op):
    if isinstance(op, ast.Constant):
        if isinstance(op.value, int):
            return [ ir.SetRegImm(result, op.value) ]
        if isinstance(op.value, str):
            global _global_counter
            _global_counter += 1
            name = f"__compiler_global_{_global_counter}"
            _globalvars[name] = op.value
            return [ ir.SetRegGlobalPtr(result, name) ]
        else:
            _assertion(False, "unsupported constant type")
    if isinstance(op, ast.Name): # variable copy
        _assertion(op.id in _func_locals, f"undefined variable {op.id}")
        return [ ir.CopyReg(_func_locals[op.id], result) ]
    if isinstance(op, ast.Call):
        return _gen_fn_call(op, result)
    if isinstance(op, ast.Subscript):
        _assertion(op.value.id in _func_locals, f"undefined variable {op.value.id}")
        regn_src = _func_locals[op.value.id]
        regn_offset = _alloc_vreg()
        return _gen_expr(regn_offset, op.slice) + [ ir.ReadPointerReg(regn_src, result, regn_offset) ]
    _assert_instance(op, ast.BinOp, f"unsupported expr {ast.dump(op)}")
    ops = [] # tuple[list[ir], int[vregn]]
    for x in [op.left, op.right]:
        if isinstance(x, ast.Name):
            _assertion(x.id in _func_locals, f"undefined variable {x.id}")
            ops.append(([], _func_locals[x.id]))
            continue
        outn = _alloc_vreg()
        ops.append((_gen_expr(outn, x), outn))
    return ops[0][0] + ops[1][0] + [ ir.ThreeAddressInstr(result, ops[0][1], ops[1][1], ir.astOp2IrOp(op.op)) ]

def _gen_fn_call(op, return_regn = None):
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
    _func_is_leaf = False # TODO: global?
    argRegs = []
    argRegIr = []
    for arg in op.args:
        reg = _alloc_vreg()
        argRegs.append(reg)
        argRegIr += _gen_expr(reg, arg)
    return argRegIr + [ir.FuncCall(op.func.id, argRegs, return_regn)]


def gen_ast_node(node, depth=0):
    global _func_locals
    global _func_is_leaf
    global _label_counter

    def print_d(s):
        print(f"{' ' * (depth*4)}{s}")

    print_d(f"irgen: {node}")

    if isinstance(node, ast.Assign):
        print_d(f"assignment {ast.dump(node)}")
        _assertion(len(node.targets) == 1, "only one assignment target supported")
        target = node.targets[0]
        _assertion(isinstance(target, ast.Name) or isinstance(target, ast.Subscript), "can only assign to names or subscripts")
        _assert_instance(target.ctx, ast.Store, "can only store assign")
        if depth == 0:  # TODO: better way to check depth
            _assert_instance(target, ast.Name, "invalid global assignment")
            _assert_instance(
                node.value, ast.Constant, "can only assign constant to globals"
            )
            _assertion(target.id not in _globalvars, "global variable already defined")
            _globalvars[target.id] = node.value.value
        else:
            if isinstance(target, ast.Subscript):
                _assertion(target.value.id in _func_locals, f"undefined variable {target.value.id}")
                regn_ptr = _func_locals[target.value.id]
                regn_offset = _alloc_vreg()
                regn_src = _alloc_vreg()
                return _gen_expr(regn_src, node.value) + _gen_expr(regn_offset, target.slice) + [ ir.WritePointerReg(regn_ptr, regn_offset, regn_src) ]
            else:
                if target.id in _func_locals:
                    n = _func_locals[target.id]
                else:
                    n = _alloc_vreg()
                    _func_locals[target.id] = n
                return _gen_expr(n, node.value)
        return []

    if isinstance(node, ast.If):
        print_d(f"if stmt {ast.dump(node)}")
        _assert_instance(node.test, ast.Compare, "unsupported if statement")
        _label_counter += 1
        lblIfTrue = f"L{_label_counter}"
        _label_counter += 1
        lblIfFalse = f"L{_label_counter}"
        _label_counter += 1
        lblIfEnd = f"L{_label_counter}"
        
        body = []
        for n in node.body:
            body += gen_ast_node(n, depth + 1)
        orelse = []
        for n in node.orelse:
            orelse += gen_ast_node(n, depth + 1)

        if isinstance(node.test, ast.Compare):
            _assertion(len(node.test.ops) == 1, "unsupported if statement")
            _assertion(len(node.test.comparators) == 1, "unsupported if statement")
            cmpr1 = _alloc_vreg()
            cmpir1 = _gen_expr(cmpr1, node.test.left)
            cmpr2 = _alloc_vreg()
            cmpir2 = _gen_expr(cmpr2, node.test.comparators[0])

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

        _label_counter += 1
        lblLoopStart = f"L{_label_counter}"
        _label_counter += 1
        lblLoopBody = f"L{_label_counter}"
        _label_counter += 1
        lblLoopEsc = f"L{_label_counter}"

        global _closestLoopEscapeLabel, _closestLoopContinueLabel

        _prev_closest_esc = _closestLoopEscapeLabel
        _prev_closest_cont = _closestLoopContinueLabel

        _closestLoopEscapeLabel = lblLoopEsc
        _closestLoopContinueLabel = lblLoopStart

        body = []
        for n in node.body:
            body += gen_ast_node(n, depth + 1)

        _closestLoopEscapeLabel = _prev_closest_esc
        _closestLoopContinueLabel = _prev_closest_cont

        _assertion(len(node.test.ops) == 1, "unsupported while loop")
        _assertion(len(node.test.comparators) == 1, "unsupported while loop")
        cmpr1 = _alloc_vreg()
        cmpir1 = _gen_expr(cmpr1, node.test.left)
        cmpr2 = _alloc_vreg()
        cmpir2 = _gen_expr(cmpr2, node.test.comparators[0])
    

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
            _assertion(var not in _func_locals, f"cannot use global {var} since it is already defined as a local")
            n = _alloc_vreg()
            _func_locals[var] = n
            body.append(ir.SetRegGlobalPtr(n, var))
        return body
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        print_d(f'expr {ast.dump(node.value)}')
        return _gen_fn_call(node.value)

    if isinstance(node, ast.Return):
        _assertion(depth > 0, "cannot return outside function")
        n = _alloc_vreg()
        return _gen_expr(n, node.value) + [ir.FuncReturnReg(n)]

    if isinstance(node, ast.Break):
        _assertion(_closestLoopEscapeLabel is not None, "invalid break")
        return [ir.JumpLocalLabel(_closestLoopEscapeLabel)]

    if isinstance(node, ast.Continue):
        _assertion(_closestLoopContinueLabel is not None, "invalid continue")
        return [ir.JumpLocalLabel(_closestLoopContinueLabel)]
    
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
        _func_locals = {}
        _func_is_leaf = True
        _label_counter = -1
        fbody = []
        for argn, arg in enumerate(node.args.args):
            _assertion(arg.arg not in _func_locals, "double argument")
            n = _alloc_vreg()
            _func_locals[arg.arg] = n
            fbody.append(ir.SetRegFuncArg(n, argn))
        for n in node.body:
            fbody += gen_ast_node(n, depth + 1)
        return [ir.Function(node.name, _func_is_leaf, len(_func_locals), len(node.args.args), fbody)]

    _assertion(False, f"cannot generate IR for AST node {ast.dump(node)}")


def gen_global_vars():
    irl = []
    for k, v in _globalvars.items():
        irl.append(ir.GlobalVarDef(k, v))
    return irl
