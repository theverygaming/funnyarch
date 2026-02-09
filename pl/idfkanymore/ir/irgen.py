from idfkanymore.parse import ast_mod
from dataclasses import dataclass
from . import lib as irlib
from . import ir

_parsers = []


def reg_ast_node_parser(c, end_only=False):
    def fn2(fn):
        _parsers.append((c, fn, end_only))
        return fn

    return fn2


@dataclass
class IrGenContext:
    datatypes = {
        "U8": ir.DatatypeSimpleInteger(8, False),
        "I8": ir.DatatypeSimpleInteger(8, True),
        "U16": ir.DatatypeSimpleInteger(16, False),
        "I16": ir.DatatypeSimpleInteger(16, True),
        "U32": ir.DatatypeSimpleInteger(32, False),
        "I32": ir.DatatypeSimpleInteger(32, True),

        "USIZE": ir.DatatypeSimpleInteger(32, False),

        "VOID": None,
    }
    globalvars = {}

    _global_counter = -1
    depth = 0

    # specific when inside procedures
    proc_locals = None
    proc_is_leaf = None
    proc_vreg_counter = None
    proc_regs = None
    proc_label_counter = None
    proc_closest_loop_escape_label = None
    proc_closest_loop_continue_label = None

    def alloc_vreg(self, t):
        self.proc_vreg_counter += 1
        self.proc_regs[self.proc_vreg_counter] = t
        return self.proc_vreg_counter

    def alloc_label(self):
        self.proc_label_counter += 1
        return self.proc_label_counter

    def lookup_type(self, ast_type):
        if isinstance(ast_type, ast_mod.TypeName):
            return self.datatypes[ast_type.name]
        elif isinstance(ast_type, ast_mod.TypePointer):
            return ir.DatatypePointer(self.lookup_type(ast_type.pointing_to))
        elif isinstance(ast_type, ast_mod.TypeArray):
            return ir.DatatypeArray(self.lookup_type(ast_type.member_type), ast_type.size)
        raise Exception(f"could not find type {ast_type}")

    def gen_ast_node(self, node, parent_nodes=None):
        if parent_nodes is None:
            parent_nodes = []

        def print_d(s):
            print(f"{' ' * (self.depth*4)}{s}")
        
        def nl_match_cls(cls_h, nodel):
            # won't work
            if len(cls_h) != len(nodel):
                return False
            # we reached the end
            if len(cls_h) == 0:
                return True
            # compare current node
            if isinstance(nodel[0], cls_h[0]):
                return nl_match_cls(cls_h[1:], nodel[1:])
            return False

        # print_d(f"irgen: {node}")

        next_parent_nodes = parent_nodes + [node]
        for cl, fn, end_only in _parsers:
            if not end_only:
                parser_matches = nl_match_cls(cl, next_parent_nodes)
            else:
                parser_matches = nl_match_cls(cl, next_parent_nodes[-len(cl):])
            if parser_matches:
                data = fn(self, node, lambda x: self.gen_ast_node(x, next_parent_nodes))
                if isinstance(data, list):
                    return data
                if isinstance(data, ir.BaseIrObj):
                    return [data]

        # FIXME: bad assert
        print_d(f"irgen MISSING {node}")
        return []
        irlib.assertion(False, f"cannot generate IR for AST node {node} parent_nodes: {parent_nodes}")

    def gen_global_vars(self):
        irl = []
        for k, v in self.globalvars.items():
            if v["def"]:
                irl.append(ir.GlobalVarDef(k, v["type"], v["value"], True))
        return irl

    @classmethod
    def from_ast(cls, ast):
        ir = []

        ctx = cls()
        for node in ast:
            ir += ctx.gen_ast_node(node)

        ir = ir + ctx.gen_global_vars()

        return ir
