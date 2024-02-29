# global variables
global1 = "this is a string\n"
global2 = """This is a
Multiline
string
"""

def read_byte_unaligned(ptr):
    # return ptr[0] & 0xFF # if the architecture supports unaligned accesses
    misalignment_bits = (ptr & 0b11) << 3
    # TODO: lang needs a way of knowing word size
    ptr_aligned = ptr & 0xFFFFFFFC
    return (ptr_aligned[0] >> misalignment_bits) & 0xFF


def puts(s):
    serial_data_reg = 0xF004B000
    c = read_byte_unaligned(s)
    while c != 0:
        serial_data_reg[0] = c
        s = s + 1
        c = read_byte_unaligned(s)


@export
def _start():
    # Use the global keyword to get a local variable with the same name as the global you are trying to access.
    # The local variable will contain a **pointer** to the global variable
    global global1, global2
    puts(global1)
    puts(global2)
    s = "some string that we will replace anyway\n"

    # dereference pointers with offset via the array subscript operator
    s[0] = (
        (ord("h") << 0)
        | (ord("i") << 8)
        | (ord("!") << 16)
    )  # ord() is a builtin, does the same thing it does in Python
    puts(s)

    x = "Local variables have function-wide scope, unlike C\n"
    puts(x)
