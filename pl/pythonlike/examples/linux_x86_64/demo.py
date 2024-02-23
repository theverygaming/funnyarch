# this code should work fine when transpiled to C and ran on x86_64

# global variables
global1 = "this is a string\n"
global2 = 'this is a string with single quotes (same as above)\n'
global3 = """This is a
Multiline
string
"""
global4 = 123 # number

def read_byte_unaligned(ptr):
    # return ptr[0] & 0xFF # if the architecture supports unaligned accesses
    misalignment_bits = (ptr & 0b11) << 3
    # TODO: lang needs a way of knowing word size
    #ptr_aligned = ptr & 0xFFFFFFFC
    ptr_aligned = ptr & 0xFFFFFFFFFFFFFFFC
    return (ptr_aligned[0] >> misalignment_bits) & 0xFF

def strlen(s):
    count = 0
    while read_byte_unaligned(s+count) != 0: # while loop, accessing arrays
        count = count + 1
    return count

def puts(s):
    do_linux_syscall(1, 1, s, strlen(s)) # calling external functions

def exit(n):
    do_linux_syscall(0x3c, n)

@export
def _start():
    # Use the global keyword to get a local variable with the same name as the global you are trying to access.
    # The local variable will contain a **pointer** to the global variable
    global global1, global2, global3
    global global4
    puts(global1)
    puts(global2)
    puts(global3)
    s = "some string that we will replace anyway\n"

    # dereference pointers with offset via the array subscript operator
    s[0] = (ord("h") << 0) | (ord("i") << 8) | (ord("i") << 16) | (ord(" ") << 24) | (ord(":") << 32) | (ord("3") << 40) # ord() is a builtin, does the same thing it does in Python
    puts(s)
    puts("\n") # functions can be called with a string as argument directly. The string will automatically be made a global variable

    if global4[0] == 121:
        global4[0] = 5
    elif global4[0] == 124:
        global4[0] = 6
    else:
        global4[0] = 6
        x = "Local variables have function-wide scope, unlike C\n"
    puts(x)
    exit(0)
