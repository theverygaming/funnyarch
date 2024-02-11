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

_closestLoopEscapeLabel = None
_closestLoopContinueLabel = None


def gen_ast_node(node, depth=0):
    global _func_locals
    global _func_is_leaf
    global _vreg_counter
    global _label_counter

    def print_d(s):
        print(f"{' ' * (depth*4)}{s}")

    print_d(f"irgen: {node}")

    if isinstance(node, ast.Assign):
        print_d(f"assignment {ast.dump(node)}")
        _assertion(len(node.targets) == 1, "only one assignment target supported")
        target = node.targets[0]
        _assert_instance(target, ast.Name, "can only assign to names")
        _assert_instance(target.ctx, ast.Store, "can only store assign")
        if depth == 0:  # TODO: better way to check depth
            _assert_instance(
                node.value, ast.Constant, "can only assign constant to globals"
            )
            _assertion(target.id not in _globalvars, "global variable already defined")
            _globalvars[target.id] = node.value.value
        else:
            _assertion(isinstance(node.value, ast.Constant) or isinstance(node.value, ast.BinOp), "unsupported local")
            def eval_bin_op(result, op):
                if isinstance(op, ast.Constant):
                    return [ ir.SetRegImm(result, op.value) ]
                _assert_instance(op, ast.BinOp, "expected BinOp")
                global _vreg_counter
                ops = [] # tuple[list[ir], int[vregn]]
                for x in [op.left, op.right]:
                    if isinstance(x, ast.Name):
                        if x.id not in _func_locals:
                            _assertion(False, f"undefined variable {x.id}")
                        ops.append(([], _func_locals[x.id]))
                        continue
                    _vreg_counter += 1
                    outn = _vreg_counter
                    ops.append((eval_bin_op(outn, x), outn))
                return ops[0][0] + ops[1][0] + [ ir.ThreeAddressInstr(result, ops[0][1], ops[1][1], ir.astOp2IrOp(op.op)) ]
            if target.id in _func_locals:
                n = _func_locals[target.id]
            else:
                _vreg_counter += 1
                n = _vreg_counter
                _func_locals[target.id] = n
            return eval_bin_op(n, node.value)
        return []

    if isinstance(node, ast.If):
        print_d(f"if stmt {ast.dump(node)}")
        _assert_instance(node.test, ast.Compare, "unsupported if statement")
        def load_var(op): # returns: (resultreg, [ir])
                global _vreg_counter
                if isinstance(op, ast.Constant):
                    _vreg_counter += 1
                    dstn = _vreg_counter
                    return (dstn, [ ir.SetRegImm(dstn, op.value) ])
                if isinstance(op, ast.Name):
                    if op.id not in _func_locals:
                        _assertion(False, f"undefined variable {op.id}")
                    return (_func_locals[op.id], [])
                else:
                    _assertion(False, f"could not load {op}")

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
            cmpr1, cmpir1 = load_var(node.test.left)
            cmpr2, cmpir2 = load_var(node.test.comparators[0])

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
        
        def load_var(op): # returns: (resultreg, [ir])
            global _vreg_counter
            if isinstance(op, ast.Constant):
                _vreg_counter += 1
                dstn = _vreg_counter
                return (dstn, [ ir.SetRegImm(dstn, op.value) ])
            if isinstance(op, ast.Name):
                if op.id not in _func_locals:
                    _assertion(False, f"undefined variable {op.id}")
                return (_func_locals[op.id], [])
            else:
                _assertion(False, f"could not load {op}")

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
        cmpr1, cmpir1 = load_var(node.test.left)
        cmpr2, cmpir2 = load_var(node.test.comparators[0])
    

        return (
            cmpir1
            + cmpir2
            + [ir.LocalLabel(lblLoopStart)]
            + [ir.Compare(cmpr1, cmpr2, ir.astCmpOp2IrCmpOp(node.test.ops[0]), lblLoopBody, lblLoopEsc)]
            + [ir.LocalLabel(lblLoopBody)]
            + body
            + [ir.JumpLocalLabel(lblLoopStart)]
            + [ir.LocalLabel(lblLoopEsc)]
            #+ orelse
        )
        

    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        _assertion(len(node.value.keywords) == 0, "no keyword arguments supported")
        _assertion(len(node.value.args) == 0, "no arguments supported")
        _assert_instance(node.value.func, ast.Name, "weird function call")
        _func_is_leaf = False
        return [ir.FuncCall(node.value.func.id)]

    if isinstance(node, ast.Return):
        def load_var(op): # returns: (resultreg, [ir])
            global _vreg_counter
            if isinstance(op, ast.Constant):
                _vreg_counter += 1
                dstn = _vreg_counter
                return (dstn, [ ir.SetRegImm(dstn, op.value) ])
            if isinstance(op, ast.Name):
                if op.id not in _func_locals:
                    _assertion(False, f"undefined variable {op.id}")
                return (_func_locals[op.id], [])
            else:
                _assertion(False, f"could not load {op}")
        reg, regir = load_var(node.value)
        return regir + [ir.FuncReturnReg(reg)]

    if isinstance(node, ast.Break):
        _assertion(_closestLoopEscapeLabel is not None, "invalid break")
        return [ir.JumpLocalLabel(_closestLoopEscapeLabel)]

    if isinstance(node, ast.Continue):
        _assertion(_closestLoopContinueLabel is not None, "invalid continue")
        return [ir.JumpLocalLabel(_closestLoopContinueLabel)]

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
            _vreg_counter += 1
            n = _vreg_counter
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
