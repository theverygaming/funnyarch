import enum
import dataclasses

class BaseIrObj:
    pass


class IrInstrObj(BaseIrObj):
    def __repr__(self):
        attrs = ""
        for i, x in enumerate(vars(self).items()):
            k, v = x
            attrs += f"{', ' if i != 0 else ''}{k}='{v}'"
        return f"{self.__class__.__name__}<{attrs}>"


@dataclasses.dataclass
class Datatype(BaseIrObj):
    pass


@dataclasses.dataclass
class DatatypePointer(Datatype):
    to: Datatype


@dataclasses.dataclass
class DatatypeSimpleInteger(Datatype):
    bits: int
    signed: bool


@dataclasses.dataclass
class DatatypeArray(Datatype):
    items: Datatype
    length: int


@dataclasses.dataclass
class GlobalVarDef(IrInstrObj):
    name: str
    type_: Datatype
    value: object
    export: bool


@dataclasses.dataclass
class Function(IrInstrObj):
    name: str
    leaf: bool
    args: list[tuple[str, Datatype]]
    return_type: Datatype
    regs: dict[int, Datatype]
    body: list[IrInstrObj]
    export: bool


@dataclasses.dataclass
class FuncReturn(IrInstrObj):
    regid_retval: int | None = None


@dataclasses.dataclass
class FuncCall(IrInstrObj):
    regid_ptr: int
    regids_args: list[int]
    regid_return: int | None = None


class CompareOperator(BaseIrObj, enum.Enum):
    EQ = 1
    NEQ = 2
    LT = 3
    LTEQ = 4
    GT = 5
    GTEQ = 6

    @classmethod
    def from_ast_op(cls, ast_op):
        transl = {
            "Eq": cls.EQ,
            "NotEq": cls.NEQ,
            "Lt": cls.LT,
            "LtE": cls.LTEQ,
            "Gt": cls.GT,
            "GtE": cls.GTEQ,
        }
        if ast_op.__class__.__name__ not in transl:
            raise Exception(f"cannot translate comparison operator {ast_op}")
        return transl[ast_op.__class__.__name__]


@dataclasses.dataclass
class Compare(IrInstrObj):
    regid_res: int
    regid_lhs: int
    op: CompareOperator
    regid_rhs: int


@dataclasses.dataclass
class LocalLabel(IrInstrObj):
    label: str


@dataclasses.dataclass
class JumpLocalLabel(IrInstrObj):
    label: str
    cond_regid: int | None = None


@dataclasses.dataclass
class SetRegImm(IrInstrObj):
    regid: int
    type_: Datatype
    value: object


@dataclasses.dataclass
class SetPtrReg(IrInstrObj):
    regid_ptr: int
    regid_index: int
    regid_value: int
    type_: Datatype


@dataclasses.dataclass
class GetPtrReg(IrInstrObj):
    regid_value: int
    regid_ptr: int
    regid_index: int
    type_: Datatype


@dataclasses.dataclass
class GetGlobalPtr(IrInstrObj):
    regid_ptr_dst: int
    name: str


@dataclasses.dataclass
class GetArgPtr(IrInstrObj):
    regid_ptr_dst: int
    arg_name: str


@dataclasses.dataclass
class GetFnPtr(IrInstrObj):
    regid_ptr_dst: int
    name: str


@dataclasses.dataclass
class CopyReg(IrInstrObj):
    regid_src: int
    regid_dst: int


class BinaryOperator(BaseIrObj, enum.Enum):
    ADD = 1
    SUB = 2
    MULT = 3
    DIV = 4
    MOD = 5
    LSHIFT = 6
    RSHIFT = 7
    OR = 8
    XOR = 9
    AND = 10

    @classmethod
    def from_ast_op(cls, ast_op):
        transl = {
            "Add": cls.ADD,
            "Sub": cls.SUB,
            "Mult": cls.MULT,
            "Div": cls.DIV,
            "Mod": cls.MOD,
            "LShift": cls.LSHIFT,
            "RShift": cls.RSHIFT,
            "BitOr": cls.OR,
            "BitXor": cls.XOR,
            "BitAnd": cls.AND,
        }
        if ast_op.__class__.__name__ not in transl:
            raise Exception(f"cannot translate operator {ast_op}")
        return transl[ast_op.__class__.__name__]


@dataclasses.dataclass
class BinOp(IrInstrObj):
    regid_result: int
    regid_lhs: int
    op: BinaryOperator
    regid_rhs: int


class UnaryOperator(BaseIrObj, enum.Enum):
    BW_NOT = 1

    @classmethod
    def from_ast_op(cls, ast_op):
        transl = {
            "Not": cls.ADD,
        }
        if ast_op.__class__.__name__ not in transl:
            raise Exception(f"cannot translate operator {ast_op}")
        return transl[ast_op.__class__.__name__]


@dataclasses.dataclass
class UnaryOp(IrInstrObj):
    regid_result: int
    op: UnaryOperator
    regid_rhs: int
