import backend
from . import codegen

@backend.reg_backend("funnyarch")
class FunnarchBackend(backend.Template):
    gen_assembly = codegen.gen_assembly
