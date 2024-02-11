import ast
import argparse
import irgen
import codegen

parser = argparse.ArgumentParser(description="Weird compiler")
parser.add_argument("infilename", metavar="input", help="input file name", type=str)
parser.add_argument("-o", "--out", metavar="out", help="output file name", required=True, type=str)
args = parser.parse_args()

with open(args.infilename, "r", encoding="utf-8") as f:
    astnodes = ast.parse(f.read()).body

    ir = []

    try:
        for node in astnodes:
            # if isinstance(node, ast.Import):
            #    continue
            ir += irgen.gen_ast_node(node)
    except Exception as e:
        print(e)

    ir = irgen.gen_global_vars() + ir

    asm = codegen.gen_assembly(ir)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(asm)
