def assertion(value, error):
    if not value:
        raise Exception("Assertion failed: " + error)


def assert_instance(o, c, errmsg):
    if not isinstance(o, c):
        print("error message: " + errmsg)
        raise Exception(f"{o} is not an instance if {c}")
