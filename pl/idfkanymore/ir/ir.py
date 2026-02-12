import enum
import dataclasses
from idfkanymore.parse import ast_mod

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
    item_type: Datatype
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
    regid_ptr: int | None
    name: str | None
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
            ast_mod.ComparisonOperatorType.EQ: cls.EQ,
            ast_mod.ComparisonOperatorType.NEQ: cls.NEQ,
            ast_mod.ComparisonOperatorType.LT: cls.LT,
            ast_mod.ComparisonOperatorType.LTEQ: cls.LTEQ,
            ast_mod.ComparisonOperatorType.GT: cls.GT,
            ast_mod.ComparisonOperatorType.GTEQ: cls.GTEQ,
        }
        if ast_op not in transl:
            raise Exception(f"cannot translate comparison operator {ast_op}")
        return transl[ast_op]


@dataclasses.dataclass
class Compare(IrInstrObj):
    regid_result: int
    regid_lhs: int
    op: CompareOperator
    regid_rhs: int


@dataclasses.dataclass
class LocalLabel(IrInstrObj):
    label: int


@dataclasses.dataclass
class JumpLocalLabel(IrInstrObj):
    label: int


@dataclasses.dataclass
class JumpLocalLabelCondTruthy(IrInstrObj):
    label: int
    cond_regid: int


@dataclasses.dataclass
class JumpLocalLabelCondFalsy(IrInstrObj):
    label: int
    cond_regid: int


@dataclasses.dataclass
class SetRegImm(IrInstrObj):
    regid: int
    value: object
    # TODO: this should probably have a type


@dataclasses.dataclass
class CopyReg(IrInstrObj):
    regid_src: int
    regid_dst: int


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
class GetArgVal(IrInstrObj):
    regid_dst: int
    arg_name: str


@dataclasses.dataclass
class GetFnPtr(IrInstrObj):
    regid_ptr_dst: int
    name: str


class BinaryOperator(BaseIrObj, enum.Enum):
    ADD = 1
    SUB = 2
    MULT = 3
    DIV = 4
    MOD = 5
    LSHIFT = 6
    RSHIFT = 7
    ARSHIFT = 8
    OR = 9
    XOR = 10
    AND = 11
    LOGICAL_AND = 12
    LOGICAL_OR = 13

    @classmethod
    def from_ast_op(cls, ast_op):
        transl = {
            ast_mod.BinaryOperatorType.PLUS: cls.ADD,
            ast_mod.BinaryOperatorType.MINUS: cls.SUB,
            ast_mod.BinaryOperatorType.MULTIPLY: cls.MULT,
            ast_mod.BinaryOperatorType.DIVIDE: cls.DIV,
            ast_mod.BinaryOperatorType.REMAINDER: cls.MOD,
            ast_mod.BinaryOperatorType.BW_SHIFT_LEFT: cls.LSHIFT,
            ast_mod.BinaryOperatorType.BW_SHIFT_RIGHT: cls.RSHIFT,
            ast_mod.BinaryOperatorType.BW_AR_SHIFT_RIGHT: cls.ARSHIFT,
            ast_mod.BinaryOperatorType.BW_OR: cls.OR,
            ast_mod.BinaryOperatorType.BW_XOR: cls.XOR,
            ast_mod.BinaryOperatorType.BW_AND: cls.AND,
            ast_mod.BinaryOperatorType.LOGICAL_AND: cls.LOGICAL_AND,
            ast_mod.BinaryOperatorType.LOGICAL_OR: cls.LOGICAL_OR,
        }
        if ast_op not in transl:
            raise Exception(f"cannot translate operator {ast_op}")
        return transl[ast_op]


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
            ast_mod.UnaryOperatorType.BW_NOT: cls.BW_NOT,
        }
        if ast_op not in transl:
            raise Exception(f"cannot translate operator {ast_op}")
        return transl[ast_op]


@dataclasses.dataclass
class UnaryOp(IrInstrObj):
    regid_result: int
    op: UnaryOperator
    regid_rhs: int


@dataclasses.dataclass
class StartUseRegs(BaseIrObj):
    regids: list[int]


@dataclasses.dataclass
class EndUseRegs(BaseIrObj):
    regids: list[int]
