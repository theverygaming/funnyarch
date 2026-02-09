from idfkanymore.parse import ast_mod
from .. import ir
from .. import lib as irlib
from .. import irgen as irgen

@irgen.reg_ast_node_parser((ast_mod.ProcedureDecl,))
def parse_procedure_decl(ctx, node, bubble):
    return []

@irgen.reg_ast_node_parser((ast_mod.ProcedureDef,))
def parse_procedure_def(ctx, node, bubble):
    for node in node.block.statements:
        bubble(node)
    return []
