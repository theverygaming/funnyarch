from enum import Enum


class BaseIrObj:
    def __repr__(self):
        attrs = ""
        for i, x in enumerate(vars(self).items()):
            k, v = x
            attrs += f"{', ' if i != 0 else ''}{k}='{v}'"
        return f"{self.__class__.__name__}<{attrs}>"


class GlobalVarDef(BaseIrObj):
    def __init__(self, name, values):
        self.name = name
        self.values = values


class Function(BaseIrObj):
    def __init__(self, name, leaf, export, nlocals, nargs, body):
        self.name = name
        self.leaf = leaf
        self.export = export
        self.nlocals = nlocals
        self.nargs = nargs
        self.body = body


class SetRegFuncArg(BaseIrObj):
    def __init__(self, regn, argn):
        self.regn = regn
        self.argn = argn


class FuncReturnReg(BaseIrObj):
    def __init__(self, regn):
        self.regn = regn


class FuncCall(BaseIrObj):
    def __init__(self, regn, arg_regns, return_regn=None):
        self.regn = regn
        self.arg_regns = arg_regns
        self.return_regn = return_regn


class CompareOperators(Enum):
    EQ = 1
    NEQ = 2
    LT = 3
    LTEQ = 4
    GT = 5
    GTEQ = 6


def astCmpOp2IrCmpOp(ast_op):
    transl = {
        "Eq": CompareOperators.EQ,
        "NotEq": CompareOperators.NEQ,
        "Lt": CompareOperators.LT,
        "LtE": CompareOperators.LTEQ,
        "Gt": CompareOperators.GT,
        "GtE": CompareOperators.GTEQ,
    }
    if ast_op.__class__.__name__ not in transl:
        raise Exception(f"cannot translate comparison operator {ast_op}")
    return transl[ast_op.__class__.__name__]


class Compare(BaseIrObj):
    def __init__(self, reg1, reg2, op, lblIfTrue, lblIfFalse):
        self.reg1 = reg1
        self.reg2 = reg2
        self.op = op
        self.lblIfTrue = lblIfTrue
        self.lblIfFalse = lblIfFalse


class LocalLabel(BaseIrObj):
    def __init__(self, label):
        self.label = label


class JumpLocalLabel(BaseIrObj):
    def __init__(self, label):
        self.label = label


class SetRegImm(BaseIrObj):
    def __init__(self, regn, value):
        self.regn = regn
        self.value = value


class SetRegGlobalPtr(BaseIrObj):
    def __init__(self, regn, globalname):
        self.regn = regn
        self.globalname = globalname


class ReadPointerReg(BaseIrObj):
    def __init__(self, regn_ptr, regn_dst, regn_offset):
        self.regn_ptr = regn_ptr
        self.regn_dst = regn_dst
        self.regn_offset = regn_offset


class WritePointerReg(BaseIrObj):
    def __init__(self, regn_ptr, regn_offset, regn_src):
        self.regn_ptr = regn_ptr
        self.regn_offset = regn_offset
        self.regn_src = regn_src


class CopyReg(BaseIrObj):
    def __init__(self, regn_src, regn_dst):
        self.regn_src = regn_src
        self.regn_dst = regn_dst


class ThreeAddressInstr(BaseIrObj):
    def __init__(self, result, arg1, arg2, op):
        self.result = result
        self.arg1 = arg1
        self.arg2 = arg2
        self.op = op


class Operators(Enum):
    # two args
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


def astOp2IrOp(ast_op):
    transl = {
        "Add": Operators.ADD,
        "Sub": Operators.SUB,
        "Mult": Operators.MULT,
        "Div": Operators.DIV,
        "Mod": Operators.MOD,
        "LShift": Operators.LSHIFT,
        "RShift": Operators.RSHIFT,
        "BitOr": Operators.OR,
        "BitXor": Operators.XOR,
        "BitAnd": Operators.AND,
    }
    if ast_op.__class__.__name__ not in transl:
        raise Exception(f"cannot translate operator {ast_op}")
    return transl[ast_op.__class__.__name__]
