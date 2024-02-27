pk_cursor = 0


def scroll():
    screen_ptr = 0xB8000
    cursor = 80 * 2
    while cursor < (80 * 25 * 2):
        write_byte_unaligned(
            screen_ptr + (cursor - 80 * 2), read_byte_unaligned(screen_ptr + cursor)
        )
        if (cursor / (80 * 2)) == 24:
            write_byte_unaligned(screen_ptr + cursor, 0)
        cursor = cursor + 1


@export
def kputc(c):
    global pk_cursor
    ia32_outb(0xE9, c)
    screen_ptr = 0xB8000
    if c == ord("\n"):
        pk_cursor[0] = ((pk_cursor[0] / 80) + 1) * 80
        if pk_cursor[0] >= (80 * 25):
            scroll()
            pk_cursor[0] = 80 * 24
        return 0
    if pk_cursor[0] >= (80 * 25):
        scroll()
        pk_cursor[0] = 80 * 24
    write_byte_unaligned(screen_ptr + (pk_cursor[0] * 2), c)
    write_byte_unaligned(screen_ptr + (pk_cursor[0] * 2) + 1, 0x07)
    pk_cursor[0] = pk_cursor[0] + 1


@export
def ia32_printk_init():
    screen_ptr = 0xB8000
    # clear screen
    cursor = 0
    while cursor < (80 * 25 * 2):
        write_byte_unaligned(screen_ptr + cursor, 0)
        cursor = cursor + 1
