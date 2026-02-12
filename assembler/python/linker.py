class Linker:
    def __init__(self, ld_def, sections, symbols, relocations):
        self.ld_def = ld_def
        self.sections = sections
        self.symbols = symbols
        self.relocations = relocations
    
    def link(self):
        self._relocate()

    def dump_all(self, outfile):
        for sec in self.ld_def["sections"]:
            self.dump_section(sec["name"], outfile)
    
    def dump_section(self, section, outfile):
        outfile.write(self.sections[section]["data"])

    def _get_section_offset(self, secname):
        current = self.ld_def["start"]
        for sec in self.ld_def["sections"]:
            if sec["name"] == secname:
                return current
            current += len(self.sections[sec["name"]]["data"])
        raise Exception(f"could not find offset for section {section}") 

    def _find_sym(self, symname):
        if not any([x for x in self.symbols if x.symname == symname]):
            raise Exception(f'invalid symbol "{symname}"')
        symbol = [x for x in self.symbols if x.symname == symname][0]
        return symbol
    
    def _write_uint_section(self, secname, offset, bytes_, num):
        num &= (1 << (bytes_ * 8)) - 1
        self.sections[secname]["data"][offset:offset + bytes_] = num.to_bytes(bytes_, "little")

    def _read_uint_section(self, secname, offset, bytes_):
        return int.from_bytes(self.sections[secname]["data"][offset:offset + bytes_], "little", signed=False)

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
