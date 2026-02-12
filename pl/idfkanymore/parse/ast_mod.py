from typing import Union
import dataclasses
import lark
import lark.tree
import lark.ast_utils
import enum

class ComparisonOperatorType(enum.Enum):
    LT = "<"
    GT = ">"
    LTEQ = "<="
    GTEQ = ">="
    EQ = "=="
    NEQ = "!="

class BinaryOperatorType(enum.Enum):
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    REMAINDER = "%"
    BW_SHIFT_LEFT = "<<"
    BW_SHIFT_RIGHT = ">>"
    BW_AR_SHIFT_RIGHT = ">>>"
    BW_AND = "&"
    BW_OR = "|"
    BW_XOR = "^"
    LOGICAL_AND = "&&"
    LOGICAL_OR = "||"

class UnaryOperatorType(enum.Enum):
    BW_NOT = "~"

class _Ast(lark.ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

class Statement(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

@dataclasses.dataclass
class Identifier(_Ast):
    name: str

@dataclasses.dataclass
class ImportStmt(_Ast):
    path: str

class Expression(_Ast):
    pass

@dataclasses.dataclass
class Variable(Identifier, Expression):
    def __init__(self, name: Identifier):
        self.name = name.name

class TypeBase(_Ast):
    pass

@dataclasses.dataclass
class TypeName(TypeBase):
    name: str

    def __init__(self, name: Identifier):
        self.name = name.name

@dataclasses.dataclass
class TypePointer(TypeBase):
    pointing_to: TypeBase

@dataclasses.dataclass
class TypeArray(TypeBase):
    size: int
    member_type: TypeBase

    def __init__(self, size, member_type):
        self.size = int(size)
        self.member_type = member_type

@dataclasses.dataclass
class Attribute(_Ast):
    name: str
    args: list[str | int]

    def __init__(self, name: Identifier, *args):
        self.name = name.name
        self.args = []
        for arg in args:
            if isinstance(arg, Identifier):
                self.args.append(arg.name)
                continue
            self.args.append(arg)

@dataclasses.dataclass
class Attributes(_Ast):
    attributes: list[Attribute]

    def __init__(self, *args):
        self.attributes = list(args)

@dataclasses.dataclass
class Globalvar(_Ast):
    # FIXME: visibility (export?)
    attributes: list[Attribute]
    name: str
    type_: TypeBase
    value: Expression

    def __init__(self, attributes: Attributes, name: Identifier, type_: TypeBase, value: Expression):
        self.attributes = attributes.attributes
        self.name = name.name
        self.type_ = type_
        self.value = value

@dataclasses.dataclass
class GlobalvarDecl(_Ast):
    attributes: list[Attribute]
    name: str
    type_: TypeBase

    def __init__(self, attributes: Attributes, name: Identifier, type_: TypeBase):
        self.attributes = attributes.attributes
        self.name = name.name
        self.type_ = type_

@dataclasses.dataclass
class Block(_Ast, lark.ast_utils.AsList):
    # Corresponds to code_block in the grammar
    statements: list[Statement]

@dataclasses.dataclass
class ProcedurePrototypeArg(_Ast):
    name: str
    type_: TypeBase

    def __init__(self, name: Identifier, type_: TypeBase):
        self.name = name.name
        self.type_ = type_

@dataclasses.dataclass
class ProcedurePrototype(_Ast):
    attributes: list[Attribute]
    name: str
    args: list[ProcedurePrototypeArg]
    return_type: TypeBase

    def __init__(self, attributes: Attributes, name: Identifier, *args):
        self.attributes = attributes.attributes
        self.name = name.name
        self.args = args[:-1]
        self.return_type = args[-1]

@dataclasses.dataclass
class ProcedureDefVar(_Ast):
    name: str
    type_: TypeBase

    def __init__(self, name: Identifier, type_: TypeBase):
        self.name = name.name
        self.type_ = type_

@dataclasses.dataclass
class ProcedureDef(_Ast):
    # FIXME: visibility (export?)
    prototype: ProcedurePrototype
    vars_: list[ProcedureDefVar]
    block: Block

    def __init__(self, prototype: ProcedurePrototype, *args):
        self.prototype = prototype
        self.vars_ = args[:-1]
        self.block = args[-1]

@dataclasses.dataclass
class ProcedureDecl(_Ast):
    prototype: ProcedurePrototype

@dataclasses.dataclass
class PointerIndex(Expression):
    var: str
    index_exp: Expression

    def __init__(self, var: Identifier, index_exp: Expression):
        self.var = var.name
        self.index_exp = index_exp

@dataclasses.dataclass
class ArrayDef(Expression):
    values: list[Expression]

    def __init__(self, *args):
        self.values = list(args)

@dataclasses.dataclass
class Assignment(Statement):
    to: Variable | PointerIndex
    value: Expression


@dataclasses.dataclass
class ProcedureCall(Statement, Expression):
    name: str
    args: list[Expression]

    def __init__(self, name: Identifier, *args):
        self.name = name.name
        self.args = list(args)

@dataclasses.dataclass
class Return(Statement):
    expr: Expression

@dataclasses.dataclass
class If(Statement):
    cond: Expression
    then: Block
    elsif: list[tuple[Expression, Block]]
    else_: Block | None

    def __init__(self, *args):
        self.cond = args[0]
        self.then = args[1]
        self.elsif = []
        self.else_ = None

        # build elsif list
        idx_start = 2
        while (idx_start+1) < len(args) and isinstance(args[idx_start], Expression) and isinstance(args[idx_start + 1], Block):
            self.elsif.append((args[idx_start], args[idx_start + 1]))
            idx_start += 2
        
        # buld else
        if idx_start < len(args):
            self.else_ = args[idx_start]

@dataclasses.dataclass
class While(Statement):
    cond: Expression
    block: Block

@dataclasses.dataclass
class Binop(Expression):
    lhs: Expression
    operator: BinaryOperatorType
    rhs: Expression

    def __init__(self, lhs: Expression, operator: object, rhs: Expression):
        self.lhs = lhs
        self.operator = BinaryOperatorType(str(operator))
        self.rhs = rhs

@dataclasses.dataclass
class Unaryop(Expression):
    operator: UnaryOperatorType
    expr: Expression

    def __init__(self, operator: object, expr: Expression):
        self.operator = UnaryOperatorType(str(operator))
        self.expr = expr

@dataclasses.dataclass
class Comparison(Expression):
    lhs: Expression
    operator: BinaryOperatorType
    rhs: Expression

    def __init__(self, lhs: Expression, operator: object, rhs: Expression):
        self.lhs = lhs
        self.operator = ComparisonOperatorType(str(operator))
        self.rhs = rhs

@dataclasses.dataclass
class Constant(Expression):
    value: str | int

class ToAst(lark.Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.

    def ESCAPED_STRING(self, s):
        # Remove quotation marks
        # FIXME: escape chars?
        return s[1:-1]

    def SIGNED_INT(self, n):
        return int(n)

    def HEX_NUMBER(self, n):
        return int(n, 16)

    def IDENTIFIER(self, t):
        return Identifier(str(t))

    @lark.v_args(inline=True)
    def start(self, *args):
        return list(args)
    
    @lark.v_args(inline=True)
    def start_header(self, *args):
        return list(args)
