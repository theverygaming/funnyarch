import dataclasses

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
    symname: str
    location: int


@dataclasses.dataclass
class Section:
    data: bytearray


def to_obj_file(sections: dict[str, Section], symbols: list[Symbol], relocations: list[Relocation]):
    pass

def from_obj_file():
    pass
