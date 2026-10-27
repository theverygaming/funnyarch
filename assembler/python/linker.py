#!/usr/bin/env python3
import libobjfmt as objfmt
import libar
import json

class Linker:
    def __init__(self, ld_def):
        self.ld_def = ld_def
        self.sections = {s["name"]: objfmt.Section(bytearray()) for s in self.ld_def["sections"]}
        self.symbols = {}
        self.relocations = []
        self.whole_archive = False
        self._linked_linkonce_sections = {}

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
            new_section_name = section_name
            if section_name.startswith(".gnu.linkonce."):
                if not section_name.startswith(".gnu.linkonce.t."):
                    raise Exception(f"unsupported .gnu.linkonce section type '{section_name}'")
                new_section_name = ".text"
                if section_name in self._linked_linkonce_sections:
                    if self._linked_linkonce_sections[section_name] != section.data:
                        raise Exception(f"data in .gnu.linkonce section '{section_name}' differs")
                    # added already, no need to do anything
                    continue
                self._linked_linkonce_sections[section_name] = section.data

            if new_section_name not in self.sections:
                self.sections[new_section_name] = objfmt.Section(bytearray())

            # offset to add to new symbols / relocations
            offset_add_new = len(self.sections[new_section_name].data)

            self.sections[new_section_name].data += section.data

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
                symbol.section = new_section_name
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
                relocation.section = new_section_name
                relocation.section_offset += offset_add_new

                self.relocations.append(relocation)
                relocations.pop(i)

        if symbols:
            raise Exception(f"could not process all symbols - leftover: {symbols}")

        if relocations:
            raise Exception(f"could not process all relocations - leftover: {relocations}")

    def add_static_lib(self, data):
        objfiles = {} # dict with key filename of tuples (sections, symbols, relocations)
        for (fname, _, _, _, _, fcontent) in libar.read_ar(data):
            if fname in objfiles:
                raise Exception(f"duplicate filename '{fname}' in archive")
            objfiles[fname] = objfmt.from_obj_file_data(fcontent)
        if self.whole_archive:
            for fname, objfile in objfiles.items():
                print(f"adding archive member '{fname}'")
                self.add_input(*objfile)
            return
        while True:
            objs_added = 0
            unresolved = set(self._get_unresolved_symbol_names())
            for fname, (sections, symbols, relocations) in list(objfiles.items()):
                if len(unresolved.intersection(symbols.keys())) == 0:
                    continue
                print(f"adding archive member '{fname}'")
                self.add_input(sections, symbols, relocations)
                # update unresolved, we may be able to resolve more from the freshly added object files in this same run
                unresolved = set(self._get_unresolved_symbol_names())
                objs_added += 1
                del objfiles[fname]
            if objs_added == 0:
                break

    def _get_unresolved_symbol_names(self):
        referenced = set()
        for reloc in self.relocations:
            if isinstance(reloc, objfmt.RelocationSymbol):
                referenced.add(reloc.symbol)
            elif isinstance(reloc, objfmt.RelocationSymbolDiff):
                referenced.add(reloc.symbola)
                referenced.add(reloc.symbolb)
            else:
                raise Exception(f"unknown relocation type {relocation}")
        syms = set(list(self.symbols.keys()) + [anchor["name"] for anchor in self.ld_def["anchor_symbols"]])
        return list(referenced - syms)

    def link(self):
        # TODO: when we have sections at arbitiary locations in memory, check if any sections overlap in memory (due to their size) here!
        unresolved = self._get_unresolved_symbol_names()
        if unresolved:
            raise Exception(f"unresolved symbols: {', '.join(unresolved)}")
        self._relocate()

    def dump_obj_relocatable(self, outfile):
        objfmt.to_obj_file(self.sections, self.symbols, self.relocations, outfile)

    def dump_obj_nonrelocatable(self, outfile):
        legal_sections = [sec["name"] for sec in self.ld_def["sections"]]
        objfmt.to_obj_file(
            {k: v for k, v in self.sections.items() if k in legal_sections},
            {k: v for k, v in self.symbols.items() if v.section in legal_sections},
            [],
            outfile,
        )

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
        def _reloc_get_symloc(symname):
            symbol = self._find_sym(symname)
            symval = self._get_section_offset(symbol.section) + symbol.section_offset
            return symval

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
            # FIXME: so relocate can safely run multiple times, this should NOT write self.symbols (unless
            # we are producing a relocatable object!!!) and instead keep symbols in some
            # local var.. this would also solve overriding weak symbols :)
            print(f"anchor in '{section}' at {section_offset} name {symname}")
            self.symbols[symname] = objfmt.Symbol(
                section=section,
                section_offset=section_offset,
                local=False,
                weak=False,
                common=False,
                common_size=None,
            )

        # compute section base addrs
        for secname, sec in self.sections.items():
            baseaddr = self._get_section_offset(secname)
            sec.base_addr = baseaddr

        # compute all symbol values
        for symname, sym in self.symbols.items():
            sym.value = _reloc_get_symloc(symname)

        # and finally, relocate!
        for reloc in self.relocations:
            relocval = 0

            if isinstance(reloc, objfmt.RelocationSymbol):
                symbol_loc = _reloc_get_symloc(reloc.symbol) + reloc.offset
                if reloc.pcrel:
                    reloc_section_offset = self._get_section_offset(reloc.section) + reloc.section_offset
                    relocval = symbol_loc - (reloc_section_offset + 4)
                else:
                    relocval = symbol_loc
            elif isinstance(reloc, objfmt.RelocationSymbolDiff):
                symbola_loc = _reloc_get_symloc(reloc.symbola)
                symbolb_loc = _reloc_get_symloc(reloc.symbolb)
                relocval = symbola_loc - symbolb_loc
            else:
                raise Exception(f"unknown relocation type {reloc}")
            
            if reloc.pre1_rshift is not None:
                relocval >>= reloc.pre1_rshift
            if reloc.pre2_mask is not None:
                relocval &= reloc.pre2_mask

            if relocval > pow(2, reloc.dst_bits):
                raise Exception(f"relocation {reloc} does not fit")

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

    parser = argparse.ArgumentParser(description="Weird compiler")
    parser.add_argument(
        "--origin", metavar="origin", help="origin", default=0, type=int
    )
    parser.add_argument(
        "-o", "--output", metavar="output", help="output file name", required=True, type=str
    )
    parser.add_argument(
        "-r", "--relocatable", help="produce a relocatable object file as output", action="store_true"
    )
    parser.add_argument(
        "-T", "--script", metavar="script", help="linker script (JSON)", type=str
    )
    args, remaining_args = parser.parse_known_args()

    ldscript = {
        "start": args.origin,
        "sections": [
            {"name": ".entry"},
            {"name": ".text"},
            {"name": ".rodata"},
            {"name": ".data"},
            {"name": ".bss"},
        ],
        "anchor_symbols": [],
    }
    if args.script:
        print(f"using linker script '{args.script}'")
        with open(args.script, "r", encoding="utf-8") as f:
            ldscript = json.loads(f.read())

    ld = Linker(ldscript)

    for inf in remaining_args:
        if inf == "--whole-archive":
            ld.whole_archive = True
            continue
        elif inf == "--no-whole-archive":
            ld.whole_archive = False
            continue
        print(f"adding input file {inf}")
        with open(inf, "rb") as f:
            data = f.read()
            if libar.detect_ar_header(data):
                ld.add_static_lib(data)
            else:
                ld.add_input(*objfmt.from_obj_file_data(data))

    if not args.relocatable:
        ld.link()

    with open(args.output, "w+b") as f:
        if args.relocatable:
            ld.dump_obj_relocatable(f)
        else:
            ld.dump_obj_nonrelocatable(f)
            #ld.write_bin(f)
