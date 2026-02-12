import objfmt

class Linker:
    def __init__(self, ld_def):
        self.ld_def = ld_def
        self.sections = {s["name"]: objfmt.Section(bytearray()) for s in self.ld_def["sections"]}
        self.symbols = {}
        self.relocations = []

    def add_input(self, sections, symbols, relocations):
        for section_name, section in sections.items():
            if section_name not in self.sections:
                raise Exception(f"file added with unknown section '{section_name}'")

            # offset to add to new symbols / relocations
            offset_add_new = len(self.sections[section_name].data)

            self.sections[section_name].data += section.data

            for symbol_name, symbol in list(symbols.items()):
                if symbol.section != section_name:
                    continue
                if symbol_name in self.symbols:
                    raise Exception(f"duplicate symbol '{symbol_name}'")

                # fixup symbol
                symbol.location += offset_add_new

                self.symbols[symbol_name] = symbol

                del symbols[symbol_name]

            i = 0
            while i < len(relocations):
                relocation = relocations[i]
                if relocation.section != section_name:
                    i += 1
                    continue

                # fixup relocation
                relocation.valueloc += offset_add_new

                self.relocations.append(relocation)
                relocations.pop(i)

        if symbols:
            raise Exception(f"could not process all symbols - leftover: {symbols}")

        if relocations:
            raise Exception(f"could not process all relocations - leftover: {relocations}")

    def link(self):
        # TODO: when we have sections at arbitiary locations in memory, check if any sections overlap in memory (due to their size) here!
        self._relocate()

    def dump_all(self, outfile):
        for sec in self.ld_def["sections"]:
            self.dump_section(sec["name"], outfile)

    def dump_section(self, section, outfile):
        outfile.write(self.sections[section].data)

    def _get_section_offset(self, secname):
        current = self.ld_def["start"]
        for sec in self.ld_def["sections"]:
            if sec["name"] == secname:
                return current
            current += len(self.sections[sec["name"]].data)
        raise Exception(f"could not find offset for section {section}") 

    def _find_sym(self, symname):
        if symname not in self.symbols:
            raise Exception(f'invalid symbol "{symname}"')
        symbol = self.symbols[symname]
        return symbol

    def _write_uint_section(self, secname, offset, bytes_, num):
        num &= (1 << (bytes_ * 8)) - 1
        self.sections[secname].data[offset:offset + bytes_] = num.to_bytes(bytes_, "little")

    def _read_uint_section(self, secname, offset, bytes_):
        return int.from_bytes(self.sections[secname].data[offset:offset + bytes_], "little", signed=False)

    def _relocate(self):
        for reloc in self.relocations:
            symbol = self._find_sym(reloc.symname)
            symloc = self._get_section_offset(symbol.section) + symbol.location
            reloc_valueloc = self._get_section_offset(reloc.section) + reloc.valueloc

            relocval = 0
            if reloc.isrelative:
                relocval = symloc - (reloc_valueloc + 4)
            else:
                relocval = symloc
            if reloc.divideval:
                relocval = int(relocval / 4)  # depends on instruction..
                print("reloc div")

            print(f"reloc sym: {reloc.symname} val: {relocval}")

            if relocval > pow(2, reloc.bits):
                raise Exception(f"relocation does not fit")

            value = self._read_uint_section(reloc.section, reloc.valueloc, 4)
            mask = (1 << reloc.bits) - 1
            value = (value & ~(mask << reloc.shift_offset)) | (
                (relocval & mask) << reloc.shift_offset
            )
            self._write_uint_section(reloc.section, reloc.valueloc, 4, value)
        self.relocations = []

if __name__ == "__main__":
    import argparse
    import objfmt

    parser = argparse.ArgumentParser(description="Weird compiler")
    parser.add_argument(
        "--origin", metavar="origin", help="origin", default=0, type=int
    )
    parser.add_argument(
        "-o", "--output", metavar="output", help="output file name", required=True, type=str
    )
    parser.add_argument("input", metavar="input", help="input file names", type=str, nargs="+")
    args = parser.parse_args()

    ld = Linker(
        {
            "start": args.origin,
            "sections": [
                {"name": ".entry"},
                {"name": ".text"},
                {"name": ".rodata"},
                {"name": ".data"},
            ],
        },
    )

    for inf in args.input:
        print(f"adding input file {inf}")
        with open(inf, "rb") as f:
            ld.add_input(*objfmt.from_obj_file(f))

    ld.link()

    with open(args.output, "w+b") as f:
        ld.dump_all(f)
