import sys
import ast
import irgen
import codegen

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} inputfile")
    exit(1)

with open(sys.argv[1], "r") as f:
    astnodes = ast.parse(f.read()).body
    
    ir = []

    try:
        for node in astnodes:
            #if isinstance(node, ast.Import):
            #    continue
            ir += irgen.gen_ast_node(node)
    except Exception as e:
        print(e)

    ir += irgen.gen_global_vars()

    print(f"global variables: {irgen.gen_global_vars()}")
    print(ir)
    asm = codegen.gen_assembly(ir)
    print("generated assembly:")
    print(asm)
