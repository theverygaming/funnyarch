import collections
from enum import Enum
import enum
import lang


class AstNodeType(Enum):
    HEAD = enum.auto()
    FUNCTION = enum.auto()
    VARIABLE = enum.auto()
    ASSIGNMENT = enum.auto()
    BIN_OP = enum.auto()
    COMPARISON = enum.auto()
    CONSTANT = enum.auto()


GlobalVariable = collections.namedtuple("GlobalVariable", ["static", "value"])

ParserPattern = collections.namedtuple("ParserPattern", ["tokens", "matched"])


def _get_possible_patterns():
    patterns = []
    patterns += [
        ParserPattern([[(lang.TokenType.KEYWORD, lang.Keyword.STATIC)], [(lang.TokenType.KEYWORD, lang.Keyword.GLOBAL)]], lambda: print("static global")),
        ParserPattern([[(lang.TokenType.KEYWORD, lang.Keyword.STATIC)], [(lang.TokenType.KEYWORD, lang.Keyword.GLOBAL)]], lambda: print("global"))
    ]
    return patterns

def gen_ast(tokens):
    ast = {"type": AstNodeType.HEAD, "children": []}
    globals = {}

    # TODO: some sort of pattern matching system instead of an if chain..
    # scope (global, func), or tokens, n tokens.. 

    idx = 0
    while idx < len(tokens):
        def assert_token(*tks):
            assert (idx+(len(tks))) < len(tokens)
            for i, t in enumerate(tks):
                for tt, tv in t:
                    assert tokens[idx+i].type == tt and tokens[idx+i].value == tv
        def check_token(*tks):
            assert (idx+(len(tks))) < len(tokens)
            for i, t in enumerate(tks):
                for tt, tv in t:   
                    if not (tokens[idx+i].type == tt and tokens[idx+i].value == tv):
                        return False
            return True
        if check_token([(lang.TokenType.KEYWORD, lang.Keyword.STATIC)], [(lang.TokenType.KEYWORD, lang.Keyword.GLOBAL)]):
            print("WOOO")
            idx += 2
            continue
        if check_token([(lang.TokenType.KEYWORD, lang.Keyword.GLOBAL)]):
            print("WOOO2")
            idx += 1
            continue

        idx += 1

    print(globals)

    return ast
