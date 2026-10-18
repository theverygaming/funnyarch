import dataclasses
import json


class DictSerializable:
    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@dataclasses.dataclass
class Relocation(DictSerializable):
    _reloc_classes = {}

    def to_dict(self):
        reloc_classes_rev = {v: k for k, v in Relocation._reloc_classes.items()}
        return {"type": reloc_classes_rev[self.__class__], "obj": dataclasses.asdict(self)}

    @classmethod
    def from_dict(cls, d):
        return Relocation._reloc_classes[d["type"]](**d["obj"])
    
    def __init_subclass__(cls, /, name, **kwargs):
        super().__init_subclass__(**kwargs)
        Relocation._reloc_classes[name] = cls

    section: str # section the relocation is in
    section_offset: int # offset of the relocation within a section
    pre1_rshift: int | None # preprocessing step 1: right shift
    pre2_mask: int | None # preprocessing step 2: mask
    dst_bits: int # width of the destination slot in bits
    dst_shift_offset: int | None # how many bits to left shift the value before fitting it into the destination slot


@dataclasses.dataclass
class RelocationSymbol(Relocation, name="sym"):
    symbol: str
    offset: int
    pcrel: bool


@dataclasses.dataclass
class RelocationSymbolDiff(Relocation, name="symdiff"):
    # operation: val = symbola - symbolb
    symbola: str
    symbolb: str


@dataclasses.dataclass
class Symbol(DictSerializable):
    section: str
    section_offset: int | None
    local: bool # only visible to the same translation unit
    weak: bool # maybe be overridden by non-weak symbols. If there is multiple weak symbols the linker will ignore anything but the first one. 
    common: bool # common symbol, these will be merged if they appear in multiple translation units. The largest one dictates the size. The section_offset is ignored for common symbols.
    common_size: int | None # size of common symbol data area.


@dataclasses.dataclass
class Section:
    data: bytearray


def to_obj_file(sections: dict[str, Section], symbols: dict[str, Symbol], relocations: list[Relocation], fileobj):
    meta_d = {
        "sections": [{"name": k, "length": len(v.data)} for k, v in sections.items()],
        "symbols": {k: v.to_dict() for k, v in symbols.items()},
        "relocations": [r.to_dict() for r in relocations],
    }
    meta = json.dumps(meta_d, separators=(',', ':')).encode("utf-8")
    fileobj.write(len(meta).to_bytes(4, "little", signed=False))
    fileobj.write(meta)
    for section in meta_d["sections"]:
        fileobj.write(sections[section["name"]].data)


def from_obj_file(fileobj) -> tuple[dict[str, Section], list[Symbol], list[Relocation]]:
    data = fileobj.read()
    len_meta = int.from_bytes(data[0:4], "little", signed=False)
    meta = json.loads(data[4:4 + len_meta].decode("utf-8"))

    sections = {}
    dptr = 4 + len_meta
    for section in meta["sections"]:
        slen = section["length"]
        sections[section["name"]] = Section(data[dptr:dptr+slen])
        dptr += slen

    symbols = {k: Symbol.from_dict(v) for k, v in meta["symbols"].items()}
    relocations = [Relocation.from_dict(r) for r in meta["relocations"]]

    return (sections, symbols, relocations)
