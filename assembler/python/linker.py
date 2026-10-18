#!/usr/bin/env python3
import objfmt

class Linker:
    def __init__(self, ld_def):
        self.ld_def = ld_def
        self.sections = {s["name"]: objfmt.Section(bytearray()) for s in self.ld_def["sections"]}
        self.symbols = {}
        self.relocations = []

    def add_input(self, sections, symbols, relocations):
        # FIXME: local syms should be handled in a less silly way lol
        localprefix = str(abs(hash(str(sections) + str(symbols))))
        symbols_copy = dict(symbols)
        def _fixup_localsym_name(oldsymname):
            # FIXME: local syms should be handled in a less silly way lol
            if oldsymname in symbols_copy and symbols_copy[oldsymname].local:
                return localprefix + oldsymname
            return oldsymname
        for section_name, section in sections.items():
            if section_name not in self.sections:
                raise Exception(f"file added with unknown section '{section_name}'")

            # offset to add to new symbols / relocations
            offset_add_new = len(self.sections[section_name].data)

            self.sections[section_name].data += section.data

            for symbol_name, symbol in list(symbols.items()):
                if symbol.section != section_name:
                    continue
                # FIXME: local syms should be handled in a less silly way lol
                oldsymbol_name = symbol_name
                if symbol.local:
                    symbol_name = localprefix + symbol_name
                # TODO: support weak symbols
                if symbol_name in self.symbols:
                    raise Exception(f"duplicate symbol '{symbol_name}'")

                # fixup symbol
                symbol.section_offset += offset_add_new

                self.symbols[symbol_name] = symbol

                del symbols[oldsymbol_name]

            i = 0
            while i < len(relocations):
                relocation = relocations[i]
                if relocation.section != section_name:
                    i += 1
                    continue

                if isinstance(relocation, objfmt.RelocationSymbol):
                    relocation.symbol = _fixup_localsym_name(relocation.symbol)
                elif isinstance(relocation, objfmt.RelocationSymbolDiff):
                    relocation.symbola = _fixup_localsym_name(relocation.symbola)
                    relocation.symbolb = _fixup_localsym_name(relocation.symbolb)
                else:
                    raise Exception(f"unknown relocation type {relocation}")

                # fixup relocation
                relocation.section_offset += offset_add_new

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
        raise Exception(f"could not find offset for section {secname}") 

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
        # handle common symbols
        for symbol in self.symbols.values():
            if not symbol.common:
                continue
            raise Exception("common symbol encountered. Unsupported!")
        
        # handle anchor symbols
        for anchor in self.ld_def["anchor_symbols"]:
            symname = anchor["name"]
            section = ""
            section_offset = 0
            if "anchor_section_start" in anchor:
                section = anchor["anchor_section_start"]
                section_offset = 0
            elif "anchor_section_end" in anchor:
                section = anchor["anchor_section_end"]
                section_offset = len(self.sections[anchor["anchor_section_end"]].data)
            else:
                raise Exception(f"bad anchor symbol: {anchor}")
            # TODO: support weak symbols
            if symname in self.symbols:
                raise Exception(f"duplicate symbol '{symname}'")
            # FIXME: so relocate can safely run multiple times, this should NOT write self.symbols and
            # instead keep symbols in some local var.. this would also solve overriding weak symbols :)
            print(f"anchor in '{section}' at {section_offset} name {symname}")
            self.symbols[symname] = objfmt.Symbol(
                section=section,
                section_offset=section_offset,
                local=False,
                weak=False,
                common=False,
                common_size=None,
            )

        for reloc in self.relocations:
            relocval = 0

            if isinstance(reloc, objfmt.RelocationSymbol):
                symbol = self._find_sym(reloc.symbol)
                symbol_loc = self._get_section_offset(symbol.section) + symbol.section_offset + reloc.offset
                if reloc.pcrel:
                    reloc_section_offset = self._get_section_offset(reloc.section) + reloc.section_offset
                    relocval = symbol_loc - (reloc_section_offset + 4)
                else:
                    relocval = symbol_loc
            elif isinstance(relocation, objfmt.RelocationSymbolDiff):
                symbola = self._find_sym(reloc.symbola)
                symbola_loc = self._get_section_offset(symbola.section) + symbola.section_offset
                symbolb = self._find_sym(reloc.symbolb)
                symbolb_loc = self._get_section_offset(symbolb.section) + symbolb.section_offset
                relocval = symbola_loc - symbolb_loc
            else:
                raise Exception(f"unknown relocation type {relocation}")
            
            if reloc.pre1_rshift is not None:
                relocval >>= reloc.pre1_rshift
            if reloc.pre2_mask is not None:
                relocval &= reloc.pre2_mask

            if relocval > pow(2, reloc.dst_bits):
                raise Exception(f"relocation {relocation} does not fit")

            value = self._read_uint_section(reloc.section, reloc.section_offset, 4)
            mask = (1 << reloc.dst_bits) - 1
            dst_shift_offset = reloc.dst_shift_offset or 0 # handle reloc.dst_shift_offset = None
            value = (value & ~(mask << dst_shift_offset)) | (
                (relocval & mask) << dst_shift_offset
            )
            self._write_uint_section(reloc.section, reloc.section_offset, 4, value)
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
            "anchor_symbols": [],
        },
    )

    for inf in args.input:
        print(f"adding input file {inf}")
        with open(inf, "rb") as f:
            ld.add_input(*objfmt.from_obj_file(f))

    ld.link()

    with open(args.output, "w+b") as f:
        ld.dump_all(f)
