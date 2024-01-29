class BaseIrObj:
    def __repr__(self):
        attrs = ""
        for i, x in enumerate(vars(self).items()):
            k, v = x
            attrs += f"{', ' if i != 0 else ''}{k}='{v}'"
        return f"{self.__class__.__name__}<{attrs}>"


class GlobalVarDef(BaseIrObj):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Function(BaseIrObj):
    def __init__(self, name, leaf, nlocals, body):
        self.name = name
        self.leaf = leaf
        self.nlocals = nlocals
        self.body = body


class FuncReturnConst(BaseIrObj):
    def __init__(self, value):
        self.value = value


class FuncCall(BaseIrObj):
    def __init__(self, name):
        self.name = name


class LoadLocalToReg(BaseIrObj):
    def __init__(self, regn, localn):
        self.regn = regn
        self.localn = localn


class SaveRegToLocal(BaseIrObj):
    def __init__(self, regn, localn):
        self.regn = regn
        self.localn = localn


class SetRegImm(BaseIrObj):
    def __init__(self, regn, value):
        self.regn = regn
        self.value = value
