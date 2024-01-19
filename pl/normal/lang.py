from enum import Enum
import enum

class Keyword(Enum):
    EXTERN = enum.auto()
    STATIC = enum.auto()
    GLOBAL = enum.auto()
    SWITCH = enum.auto()
    IF = enum.auto()
    ELIF = enum.auto()
    ELSE = enum.auto()
    WHILE = enum.auto()
    FOR = enum.auto()
    AUTO = enum.auto()
    CASE = enum.auto()
    DEFAULT = enum.auto()
    RETURN = enum.auto()

keywords = [
    ("extern", Keyword.EXTERN),
    ("static", Keyword.STATIC),
    ("global", Keyword.GLOBAL),
    ("auto", Keyword.AUTO),
    ("if", Keyword.IF),
    ("else if", Keyword.ELIF),
    ("else", Keyword.ELSE),
    ("while", Keyword.WHILE),
    ("for", Keyword.FOR),
    ("return", Keyword.RETURN),
]

class Symbol(Enum):
    COLON = enum.auto()
    SEMICOLON = enum.auto()
    COMMA = enum.auto()
    LCURLY = enum.auto()
    RCURLY = enum.auto()
    LPAREN = enum.auto()
    RPAREN = enum.auto()
    LBRACK = enum.auto()
    RBRACK = enum.auto()
    PLUS = enum.auto()
    PLUSPLUS = enum.auto()
    MINUS = enum.auto()
    MINUSMINUS = enum.auto()
    EQUALS = enum.auto()
    EQUALSEQUALS = enum.auto()
    AND = enum.auto()
    ANDAND = enum.auto()
    LESSTHAN = enum.auto()
    LESSTHANEQ = enum.auto()
    GREATERTHAN = enum.auto()
    GREATERTHANEQ = enum.auto()

symbols = [
    (":", Symbol.COLON),
    (";", Symbol.SEMICOLON),
    (",", Symbol.COMMA),
    ("{", Symbol.LCURLY),
    ("}", Symbol.RCURLY),
    ("(", Symbol.LPAREN),
    (")", Symbol.RPAREN),
    ("(", Symbol.LBRACK),
    (")", Symbol.RBRACK),
    ("+", Symbol.PLUS),
    ("++", Symbol.PLUSPLUS),
    ("-", Symbol.MINUS),
    ("--", Symbol.MINUSMINUS),
    ("=", Symbol.EQUALS),
    ("==", Symbol.EQUALSEQUALS),
    ("&", Symbol.AND),
    ("&&", Symbol.ANDAND),
    ("<", Symbol.LESSTHAN),
    ("<=", Symbol.LESSTHANEQ),
    (">", Symbol.GREATERTHAN),
    (">=", Symbol.GREATERTHANEQ),
]

class TokenType(Enum):
    KEYWORD = enum.auto()
    SYMBOL = enum.auto()
    CONSTANT = enum.auto()
    STRING = enum.auto()
    NAME = enum.auto()


# the lexer expects these to be sorted longest first
keywords.sort(key=lambda x: len(x[0]), reverse=True)
symbols.sort(key=lambda x: len(x[0]), reverse=True)
