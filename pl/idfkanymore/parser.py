import lark

from . import ast_mod

# python3 -m idfkanymore.parser

s = open("idfkanymore/header.idkh", "r").read()
parser = lark.Lark.open("idfkanymore/lang.lark", start="start_header", parser="lalr")
tree = parser.parse(s)
print(tree.pretty())


s = open("idfkanymore/lang.idk", "r").read()
parser = lark.Lark.open("idfkanymore/lang.lark", start="start", parser="lalr")
tree = parser.parse(s)
transformer = lark.ast_utils.create_transformer(ast_mod, ast_mod.ToAst())
print(tree.pretty())
print(transformer.transform(tree))
