def assertion(value, error):
    if not value:
        raise Exception("Assertion failed: " + error)
