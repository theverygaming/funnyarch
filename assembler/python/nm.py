#!/usr/bin/env python3
import libobjfmt as objfmt

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="funnyarch objcopy")
    parser.add_argument(
        "-n", "--numeric-sort", help="output format", action="store_true"
    )
    parser.add_argument(
        "-f", "--format", help="format, e.g. bsd", type=str, default="bsd"
    )
    parser.add_argument("input", help="input file names", type=str, nargs="+")
    args = parser.parse_args()

    if args.format not in ["bsd"]:
        raise Exception(f"unsupported format '{args.format}'")

    symbols = []
    for inf in args.input:
        with open(inf, "rb") as f:
            _, newsymbols, _ = objfmt.from_obj_file_data(f.read())
            symbols += list(newsymbols.items())

    if args.numeric_sort:
        symbols.sort(key=lambda x: x[1].value or 0)

    for symname, sym in symbols:
        valuestr = f"{sym.value:08x}" if sym.value is not None else " " * 8
        print(f"{valuestr} ? {symname}")
