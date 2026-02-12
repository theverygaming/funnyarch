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
    section: str
    symname: str
    valueloc: int
    isrelative: bool
    divideval: bool # if symbol value should be divided by 4
    shift_offset: int
    bits: int


@dataclasses.dataclass
class Symbol(DictSerializable):
    section: str
    location: int


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
