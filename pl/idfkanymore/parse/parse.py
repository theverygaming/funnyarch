import lark
from . import ast_mod

def to_ast(s, header=False):
    parser = lark.Lark.open("parse/lang.lark", start="start" if not header else "start_header", parser="lalr")
    transformer = lark.ast_utils.create_transformer(ast_mod, ast_mod.ToAst())
    return transformer.transform(parser.parse(s))
