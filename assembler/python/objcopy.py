#!/usr/bin/env python3
import libobjfmt as objfmt

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="funnyarch objcopy")
    parser.add_argument(
        "-O", "--output-target", help="output format", required=True, type=str
    )
    parser.add_argument("input", help="input file name", type=str)
    parser.add_argument("output", help="output file name", type=str)
    args = parser.parse_args()

    if args.output_target not in ["binary"]:
        raise Exception(f"unsupported output format {args.output_target}")

    with open(args.input, "rb") as f:
        sections, _, _ = objfmt.from_obj_file_data(f.read())

    sections_sorted = sorted(list(sections.items()), key=lambda x: x[1].base_addr)

    with open(args.output, "w+b") as f:
        for secname, sec in sections_sorted:
            print(f"dumping section '{secname}' size {len(sec.data)}")
            f.write(sec.data)
