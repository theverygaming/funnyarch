import backend
from . import codegen

@backend.reg_backend("c")
class CBackend(backend.Template):
    gen_assembly = codegen.gen_assembly
