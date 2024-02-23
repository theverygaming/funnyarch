pk_cursor = 0

def scroll():
    screen_ptr = 0xb8000
    cursor = 80*2
    while cursor < (80*25*2):
        write_byte_unaligned(screen_ptr+(cursor-80*2), read_byte_unaligned(screen_ptr+cursor))
        write_byte_unaligned(screen_ptr+cursor, 0)
        cursor = cursor + 1

def putc(c):
    global pk_cursor
    screen_ptr = 0xb8000
    if pk_cursor[0] >= (80 * 25):
        scroll()
        pk_cursor[0] = 80*24
    if c == ord("\n"):
        pk_cursor[0] = ((pk_cursor[0] / 80)+1)*80
        return 0
    write_byte_unaligned(screen_ptr+(pk_cursor[0]*2), c)
    write_byte_unaligned(screen_ptr+(pk_cursor[0]*2)+1, 0x07)
    pk_cursor[0] = pk_cursor[0] + 1

@export
def print(s):
    c = read_byte_unaligned(s)
    while c != 0:
        putc(c)
        s = s + 1
        c = read_byte_unaligned(s)
