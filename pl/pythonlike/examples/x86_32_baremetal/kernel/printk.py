@export
def print(s):
    c = read_byte_unaligned(s)
    while c != 0:
        kputc(c)
        s = s + 1
        c = read_byte_unaligned(s)

@export
def print_n_hex(n):
    kputc(ord("0"))
    kputc(ord("x"))
    # TODO: lang needs a way of knowing word size
    i = (4*2) # 8 nibbles
    while i != 0:
        j = (n >> (i-1)*4) & 0xF
        if j > 9:
            kputc(ord("a") + (j-10))
        else:
            kputc(ord("0") + j)
        i = i - 1
