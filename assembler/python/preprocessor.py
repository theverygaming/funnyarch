import os
import re


class Macro:
    def __init__(self, name, args, content, hasargs):
        self.name = name
        self.args = args  # [""]
        self.content = content
        self.hasargs = hasargs

    def __repr__(self):
        return f'macro: "{self.name}", {self.args}, "{self.content}"'


__builtin_macros = (
    Macro("__builtin_push", ["register"], "strpi rsp, register, #-4", True),
    Macro("__builtin_pop", ["register"], "ldri register, rsp, #4", True),
    Macro("__builtin_call_lbl", ["label"], "jal label", True),
    Macro("__builtin_relcall_lbl", ["label"], "rjal label", True),
    Macro("__builtin_return", [], "mov rip, lr", False),
)


def c_comment_remover(text):  # https://stackoverflow.com/a/241506
    def replacer(match):
        s = match.group(0)
        if s.startswith("/"):
            return " "
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE,
    )
    return re.sub(pattern, replacer, text)


def rmspaces(str):
    parts = re.split(r"""("[^"]*"|'[^']*')""", str)
    parts[::2] = map(lambda s: " ".join(s.split()), parts[::2])  # outside quotes
    return " ".join(parts)


def resolvemacros(str, macros_c):
    mcount = 0
    lines = []
    macros_s = []

    ismacro = False
    for line in str.splitlines():
        line = rmspaces(line)
        if ismacro:
            if line[-1] == "\\":
                line = line[:-1] + "\n"
            else:
                ismacro = False
            macros_s[-1] += line
            continue
        else:
            split = re.split(r" ", line)
            if split[0] == "#define":
                if line[-1] == "\\":
                    line = line[:-1] + "\n"
                    ismacro = True
                macros_s.append(line)
                continue
        lines.append(line)

    for macro in macros_s:
        rg_macargs = r"(#define ([A-Za-z0-9._]+)\((([A-Za-z0-9_]+(, )?)*)\) )(.+)"
        rg_macnoargs = r"(#define ([A-Za-z0-9._]+) )(.+)"
        if re.match(rg_macargs, macro, flags=re.DOTALL):
            content = re.sub(rg_macargs, r"\6", macro, flags=re.DOTALL)
            name = re.sub(rg_macargs, r"\2", macro, flags=re.DOTALL)
            args = re.split(r", ", re.sub(rg_macargs, r"\3", macro, flags=re.DOTALL))
            if args == [""]:
                args = []
            macros_c.append(Macro(name, args, content, True))
        elif re.match(rg_macnoargs, macro, flags=re.DOTALL):
            content = re.sub(rg_macnoargs, r"\3", macro, flags=re.DOTALL)
            name = re.sub(rg_macnoargs, r"\2", macro, flags=re.DOTALL)
            macros_c.append(Macro(name, [], content, False))
        else:
            raise Exception(f"invalid macro definition {macro}")

    for i, line in enumerate(lines):
        if len(line) == 0:
            continue
        for macro in macros_c:
            rg_macargs = r"\((([^,)]+(, )?)+)\)$"
            if re.match(macro.name + rg_macargs, line):
                if not macro.hasargs:
                    raise Exception(f"invalid use of macro {macro.name}: {line}")
                mcount += 1
                args = re.sub(macro.name + rg_macargs, r"\1", line).split(", ")
                if len(macro.args) != len(args):
                    raise Exception(f"invalid macro argc {line}")

                s_margs, s_args = zip(
                    *sorted(
                        zip(macro.args, args), key=lambda n: len(n[0]), reverse=True
                    )
                )

                lines[i] = macro.content
                for j, arg in enumerate(s_args):
                    lines[i] = lines[i].replace(s_margs[j], arg)

            elif re.search(rf"\b{macro.name}\b", line) is not None:
                if macro.hasargs:
                    raise Exception(f'invalid use of macro "{macro.name}": "{line}"')
                mcount += 1
                lines[i] = re.sub(rf"\b{macro.name}\b", macro.content, line)

    str = "\n".join(lines)
    return mcount, str


def resolveincludes(str, basepath):
    includeregex = r'^#include +"(?P<fname>[^"]+)".*$'
    lines = str.splitlines()
    for i, line in enumerate(lines):
        match = re.match(includeregex, line)
        if match is not None:
            with open(os.path.join(basepath, match.group("fname"))) as w:
                newstr = w.read()
            newstr = c_comment_remover(newstr)
            newstr = resolveincludes(newstr, basepath)
            lines[i] = newstr
    str = "\n".join(lines)
    return str


def preprocess(str, basepath):
    str = c_comment_remover(str)
    str = resolveincludes(str, basepath)
    macros_c = list(__builtin_macros)
    while True:
        mcount, str = resolvemacros(str, macros_c)
        if mcount == 0:
            break

    lines = str.splitlines()
    for i, line in enumerate(lines):
        lines[i] = rmspaces(line)
    str = "\n".join(lines)

    return str
