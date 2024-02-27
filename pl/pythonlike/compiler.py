import ast
import argparse
import ir.irgen as irgen
import backend.codegen as codegen


parser = argparse.ArgumentParser(description="Weird compiler")
parser.add_argument("infilename", metavar="input", help="input file name", type=str)
parser.add_argument(
    "-o", "--out", metavar="out", help="output file name", required=True, type=str
)
args = parser.parse_args()


with open(args.infilename, "r", encoding="utf-8") as f:
    astnodes = ast.parse(f.read()).body

    ir = []

    ctx = irgen.IrGenContext()
    for node in astnodes:
        ir += irgen.gen_ast_node(ctx, node)

    ir = irgen.gen_global_vars(ctx) + ir

    asm = codegen.gen_assembly(ir)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(asm)
