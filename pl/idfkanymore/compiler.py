import argparse
import pathlib
#import ir.irgen as irgen
#import backend
from parse import parse


parser = argparse.ArgumentParser(description="Weird compiler")
parser.add_argument("infilename", metavar="input", help="input file name", type=str)
parser.add_argument(
    "-o", "--out", metavar="out", help="output file name", required=True, type=str
)
parser.add_argument(
    "--target", metavar="target", help="target backend name", required=True, type=str
)
args = parser.parse_args()

"""
target_be = backend.get_backend(args.target)
if target_be is None:
    raise Exception(f"Backend '{args.target}' not found")
else:
    target_be = target_be()

with open(args.infilename, "r", encoding="utf-8") as f:
    astnodes = ast.parse(f.read()).body

    ir = []

    ctx = irgen.IrGenContext()
    for node in astnodes:
        ir += irgen.gen_ast_node(ctx, node)

    ir = irgen.gen_global_vars(ctx) + ir

    asm = target_be.gen_assembly(ir)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(asm)
"""

with open(args.infilename, "r", encoding="utf-8") as f:
    prev_imported_paths = set()
    def _import(name):
        p = (pathlib.Path(args.infilename).parent / name).resolve(strict=True)
        if p in prev_imported_paths:
            return ""
        prev_imported_paths.add(p)
        with open(p, "r", encoding="utf-8") as f:
            return f.read()

    ast = parse.full_ast(f.read(), _import)
    print(ast)
