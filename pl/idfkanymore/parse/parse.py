import lark
from . import ast_mod

def to_ast(s, header=False):
    parser = lark.Lark.open("parse/lang.lark", start="start" if not header else "start_header", parser="lalr")
    transformer = lark.ast_utils.create_transformer(ast_mod, ast_mod.ToAst())
    return transformer.transform(parser.parse(s))

def resolve_imports(ast, import_fn):
    i = 0
    while i < len(ast):
        node = ast[i]
        if isinstance(node, ast_mod.ImportStmt):
            new_ast = resolve_imports(to_ast(import_fn(node.path), header=True), import_fn)
            ast = ast[0:i+1] + new_ast + ast[i+1:]
            ast.pop(i)
            i += len(new_ast)
            continue
        i += 1
    return ast

def full_ast(s, import_fn):
    return resolve_imports(to_ast(s), import_fn)
