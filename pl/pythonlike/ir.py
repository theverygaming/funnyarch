class BaseInstr:
    def __repr__(self):
        attrs = ""
        for i, x in enumerate(vars(self).items()):
            k, v = x
            attrs += f"{', ' if i != 0 else ''}{k}='{v}'"
        return f"{self.__class__.__name__}<{attrs}>"


class GlobalVarDef(BaseInstr):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class FuncReturnConst(BaseInstr):
    def __init__(self, value):
        self.value = value


class Function(BaseInstr):
    def __init__(self, name, leaf, nlocals, body):
        self.name = name
        self.leaf = leaf
        self.nlocals = nlocals
        self.body = body


class FuncCall(BaseInstr):
    def __init__(self, name, nlocals):
        self.name = name
        self.nlocals = nlocals


class SetLocalConst(BaseInstr):
    def __init__(self, localn, value):
        self.localn = localn
        self.value = value
