import sys
import ast
from dataclasses import dataclass
import ir.lib as irlib
import ir.ir as ir


@dataclass
class IrGenContext:
    globalvars = {}
    func_locals = None
    func_is_leaf = False
    _vreg_counter = -1
    _label_counter = -1
    _global_counter = -1
    closestLoopEscapeLabel = None
    closestLoopContinueLabel = None
    depth = 0

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


def gen_ast_node(ctx, node):
    def print_d(s):
        print(f"{' ' * (ctx.depth*4)}{s}")

    print_d(f"irgen: {node}")

    for c, fn in _parsers:
        if isinstance(node, c):
            success, data = fn(ctx, node)
            if success:
                return data

    irlib.assertion(False, f"cannot generate IR for AST node {ast.dump(node)}")


def gen_global_vars(ctx):
    irl = []
    for k, v in ctx.globalvars.items():
        irl.append(ir.GlobalVarDef(k, v))
    return irl
