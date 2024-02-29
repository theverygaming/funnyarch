class Template():
    def gen_assembly(irl):
        raise NotImplementedError()

_backends = {}

def reg_backend(name):
    def fn(cl):
        if name.lower() in _backends:
            raise Exception(f"Backend conflict, backend '{name.lower()}' already exists")
        _backends[name.lower()] = cl
        return cl
    return fn

def get_backend(name):
    return _backends.get(name.lower())
