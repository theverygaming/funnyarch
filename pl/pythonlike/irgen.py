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


def gen_ast_node(node, depth=0):
    global _func_locals
    global _func_is_leaf
    global _vreg_counter

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
            _assert_instance(
                node.value, ast.Constant, "can only assign constant to locals"
            )
            if target.id in _func_locals:
                n = _func_locals[target.id]
            else:
                n = len(_func_locals)
                _func_locals[target.id] = n
            _vreg_counter += 1
            return [ir.LoadLocalToReg(_vreg_counter, n), ir.SetRegImm(_vreg_counter, node.value.value), ir.SaveRegToLocal(_vreg_counter, n)]
        return []

    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        _assertion(len(node.value.keywords) == 0, "no keyword arguments supported")
        _assertion(len(node.value.args) == 0, "no arguments supported")
        _assert_instance(node.value.func, ast.Name, "weird function call")
        _func_is_leaf = False
        return [ir.FuncCall(node.value.func.id)]

    if isinstance(node, ast.Return):
        _assert_instance(node.value, ast.Constant, "can only return const")
        return [ir.FuncReturnConst(node.value.value)]

    if (
        isinstance(node, ast.FunctionDef) and depth == 0
    ):  # TODO: better way to check depth
        print_d(f'function definition "{node.name}" args: {ast.dump(node.args)}')
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
        fbody = []
        for n in node.body:
            fbody += gen_ast_node(n, depth + 1)
        return [ir.Function(node.name, _func_is_leaf, len(_func_locals), fbody)]

    _assertion(False, f"cannot generate IR for AST node {ast.dump(node)}")


def gen_global_vars():
    irl = []
    for k, v in _globalvars.items():
        irl.append(ir.GlobalVarDef(k, v))
    return irl
