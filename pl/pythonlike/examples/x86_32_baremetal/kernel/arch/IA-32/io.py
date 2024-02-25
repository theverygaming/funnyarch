@export
def ia32_io_wait():
    ia32_outb(0x80, 0)
