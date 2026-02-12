from idfkanymore.parse import ast_mod
from .. import ir
from .. import lib as irlib
from .. import irgen as irgen

@irgen.reg_ast_node_parser((ast_mod.GlobalvarDecl,))
def parse_globalvar_decl(ctx, node, bubble):
    t = ctx.lookup_type(node.type_)
    if node.name in ctx.globalvars:
        irlib.assertion(ctx.globalvars[node.name]["type"] == t, f"global {node.name} declared or defined with a different type")
        return []
    ctx.globalvars[node.name] = {
        "type": t,
        "def": False,
    }
    return []

def _compute_constant_expr(node):
    if isinstance(node, ast_mod.Constant):
        return node.value
    if isinstance(node, ast_mod.Binop):
        lhs = _compute_constant_expr(node.lhs)
        rhs = _compute_constant_expr(node.rhs)
        match node.operator:
            case ast_mod.BinaryOperatorType.PLUS:
                return lhs + rhs
            case ast_mod.BinaryOperatorType.MINUS:
                return lhs - rhs
            case ast_mod.BinaryOperatorType.MULTIPLY:
                return lhs * rhs
            case ast_mod.BinaryOperatorType.DIVIDE:
                return int(lhs / rhs)
            case ast_mod.BinaryOperatorType.REMAINDER:
                return int(lhs % rhs)
            case ast_mod.BinaryOperatorType.BW_SHIFT_LEFT:
                return lhs << rhs
            case ast_mod.BinaryOperatorType.BW_SHIFT_RIGHT:
                return lhs >> rhs
            case ast_mod.BinaryOperatorType.BW_AND:
                return lhs & rhs
            case ast_mod.BinaryOperatorType.BW_OR:
                return lhs | rhs
            case ast_mod.BinaryOperatorType.BW_XOR:
                return lhs ^ rhs
            case ast_mod.BinaryOperatorType.LOGICAL_AND:
                return 1 if lhs and rhs else 0
            case ast_mod.BinaryOperatorType.LOGICAL_OR:
                return 1 if lhs or rhs else 0
    if isinstance(node, ast_mod.Unaryop):
        expr = _compute_constant_expr(node.expr)
        match node.operator:
            case ast_mod.UnaryOperatorType.BW_NOT:
                return ~expr # FIXME: lmao this does not work
    raise Exception(f"could not compute constant node {node}")

@irgen.reg_ast_node_parser((ast_mod.Globalvar,))
def parse_globalvar_def(ctx, node, bubble):
    t = t = ctx.lookup_type(node.type_)
    if node.name in ctx.globalvars:
        irlib.assertion(ctx.globalvars[node.name]["type"] == t, f"global {node.name} declared or defined with a different type")
        irlib.assertion(not ctx.globalvars[node.name]["def"], f"global {node.name} defined twice")
    ctx.globalvars[node.name] = {
        "type": t,
        "value": _compute_constant_expr(node.value),
        "def": True,
        "attributes": {a.name: a.args for a in node.attributes},
    }
    return []
