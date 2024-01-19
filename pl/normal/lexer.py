import io
import lang

class Token():
    def __init__(self, ttype, value):
        self.type = ttype
        self.value = value

    def __repr__(self):
        return f'lexer.Token({self.type}, "{self.value}")'

def lex(file):
    tokens = []

    file.seek(0, io.SEEK_END)
    filesize = file.tell()
    file.seek(0)
    
    while file.tell() < filesize:
        startpos = file.tell()
        if is_char_whitespace(read := file.read(1)):
            prevseperator = True
            continue
        file.seek(startpos)

        if (symbol := getkeyword(file, lang.symbols)) is not None:
            #print(f'symbol: {symbol}')
            tokens.append(Token(lang.TokenType.SYMBOL, symbol))
            continue

        if (num := getnumber(file)) is not None:
            #print(f"number: {num}")
            tokens.append(Token(lang.TokenType.CONSTANT, num))
            continue

        if (string := getstring(file)) is not None:
            #print(f'string: "{string}"')
            tokens.append(Token(lang.TokenType.STRING, string))
            continue

        if (charliteral := getcharliteral(file)) is not None:
            #print(f'character literal: {charliteral}')
            tokens.append(Token(lang.TokenType.CONSTANT, charliteral))
            continue

        if (comment := getcomment(file)) is not None:
            #print(f'comment: "{comment}"')
            continue
        
        if (keyword := getkeyword(file, lang.keywords, skip_if_alpha_after=True)) is not None:
            #print(f'keyword: {keyword}')
            tokens.append(Token(lang.TokenType.KEYWORD, keyword))
            continue

        if (name := getname(file)) is not None:
            #print(f'name: "{name}"')
            tokens.append(Token(lang.TokenType.NAME, name))
            continue

        raise Exception(f'unknown token "{file.read(1)}"')

    return tokens


def getnumber(file):
    number = None
    startpos = file.tell()
    ndigits = 0
    while is_char_digit(file.read(1)):
        ndigits += 1
    file.seek(startpos)
    if ndigits > 0:
        digits = file.read(ndigits)
        number = int(digits)
    return number

def getstring(file):
    startpos = file.tell()
    string = None
    firstchar = file.read(1)
    if firstchar == '"':
        string = ""
        while (read := file.read(1)) != "":
            if read == '"':
                break
            if read == "\\":
                string += string_get_escaped_char(file.read(1))
                continue
            string += read
    else:
        file.seek(startpos)
    return string

def getcharliteral(file):
    startpos = file.tell()
    charliteral = None
    read = file.read(1)
    if read == "'":
        charliteral = 0
        read = file.read(1)
        if read == "\\":
            charliteral = ord(string_get_escaped_char(file.read(1)))
        else:
            charliteral = ord(read)
        if file.read(1) != "'":
            raise Exception("invalid character literal")
    else:
        file.seek(startpos)
    return charliteral

def getcomment(file):
    startpos = file.tell()
    comment = None
    firstchars = file.read(2)
    if firstchars == '/*':
        comment = ""
        lastread = ""
        while (read := file.read(1)) != "":
            if (lastread + read) == "*/":
                comment = comment[:-1]
                break
            comment += read
            lastread = read
    elif firstchars == '//':
        comment = ""
        while (read := file.read(1)) != "":
            if read == "\n":
                break
            comment += read
    else:
        file.seek(startpos)
    return comment

def getkeyword(file, keywordarr, skip_if_alpha_after=False):
    startpos = file.tell()
    value = None
    for keyword, keyval in keywordarr:
        file.seek(startpos)
        read = file.read(len(keyword))
        if len(read) != len(keyword):
            continue
        curpos = file.tell()
        nextchar = file.read(1)
        if skip_if_alpha_after and len(nextchar) > 0 and is_char_alpha(nextchar):
            continue
        file.seek(curpos)
        if keyword == read:
            return keyval
            break
    file.seek(startpos)
    return value

def getname(file):
    startpos = file.tell()
    name = ""
    while (read := file.read(1)) != "":
        if not (is_char_alpha(read) or is_char_digit(read)):
            if len(name) != 0:
                file.seek(file.tell() - 1)
            break
        name += read
    if len(name) == 0:
        name = None
        file.seek(startpos)
    return name

def is_char_whitespace(char):
    return char == " " or char == "\n"

def is_char_alpha(char):
    return (ord(char) >= ord("a") and ord(char) <= ord("z")) or ord(char) >= ord("A") and ord(char) <= ord("Z")

def is_char_digit(char):
    return ord(char) >= ord("0") and ord(char) <= ord("9")

def string_get_escaped_char(escaped):
    if escaped == "n":
        return "\n"
    elif escaped == "\\":
        return escaped
    elif escaped == '"':
        return escaped
    else:
        raise Exception(f"unknown escape character '{escaped}'")
