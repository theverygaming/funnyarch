_backends = {}

def register_backend(name):
    def fn(cl):
        if name in _backends:
            raise Exception(f"Backend conflict, backend '{name}' already exists")
        _backends[name] = cl
        return cl
    return fn

def get_backend(name):
    return _backends.get(name)

class Backend():
    def gen_assembly(self, irl):
        raise NotImplementedError()
