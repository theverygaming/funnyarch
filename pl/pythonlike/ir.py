class BaseInstr():
    pass

class GlobalVarDef(BaseInstr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class FuncReturnConst():
    def __init__(self, value):
        self.value = value

class FuncBegin():
    def __init__(self, name, leaf, nlocals):
        self.name = name
        self.leaf = leaf
        self.nlocals = nlocals

class FuncEnd():
    def __init__(self, name, leaf, nlocals):
        self.name = name
        self.leaf = leaf
        self.nlocals = nlocals

class FuncCall():
    def __init__(self, name, nlocals):
        self.name = name
        self.nlocals = nlocals
