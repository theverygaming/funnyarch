import sys
import astgen
import lexer

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} inputfile")
    exit(1)

with open(sys.argv[1], "r") as f:
    tokens = lexer.lex(f)
    for token in tokens:
        print(token)
    ast = astgen.gen_ast(tokens)
    print(ast)
