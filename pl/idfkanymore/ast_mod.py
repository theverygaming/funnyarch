import dataclasses
import lark
import lark.tree
import lark.ast_utils

class _Ast(lark.ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

class _Statement(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

@dataclasses.dataclass
class Value(_Ast, lark.ast_utils.WithMeta):
    "Uses WithMeta to include line-number metadata in the meta attribute"
    meta: lark.tree.Meta
    value: object

@dataclasses.dataclass
class Name(_Ast):
    name: str

@dataclasses.dataclass
class Block(_Ast, lark.ast_utils.AsList):
    # Corresponds to code_block in the grammar
    statements: list[_Statement]

@dataclasses.dataclass
class If(_Statement):
    def __init__(self, *args, **kwargs):
        for i, arg in enumerate(args):
            print(f"ARG {i}: {arg}")
        #raise Exception(f"funny {args} {kwargs}")
    #cond: Value
    #then: Block

@dataclasses.dataclass
class IfElsif(_Statement):
    def __init__(self, *args, **kwargs):
        for i, arg in enumerate(args):
            print(f"ARG {i}: {arg}")
        raise Exception("funny")

@dataclasses.dataclass
class SetVar(_Statement):
    # Corresponds to set_var in the grammar
    name: str
    value: Value

@dataclasses.dataclass
class Print(_Statement):
    value: Value


class ToAst(lark.Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.

    def STRING(self, s):
        # Remove quotation marks
        return s[1:-1]

    def DEC_NUMBER(self, n):
        return int(n)

    @lark.v_args(inline=True)
    def start(self, *args):
        return args
