def ps2_wait_write():
    while (ia32_inb(0x64) & 0b10) != 0:
        pass


ia32_ps2_kbd_us = [
    0x0, 0x1b, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x2d, 0x3d, 0x8, 0x9, 0x71, 0x77, 0x65, 0x72, 0x74, 0x79, 0x75, 0x69, 0x6f, 0x70, 0x5b, 0x5d, 0xa, 0x0, 0x61, 0x73, 0x64, 0x66, 0x67, 0x68, 0x6a, 0x6b, 0x6c, 0x3b, 0x27, 0x60, 0x0, 0x5c, 0x7a, 0x78, 0x63, 0x76, 0x62, 0x6e, 0x6d, 0x2c, 0x2e, 0x2f, 0x0, 0x2a, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2d, 0x0, 0x0, 0x0, 0x2b, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0
]
ia32_ps2_kbd_us_sh = [
    0x0, 0x1b, 0x21, 0x40, 0x23, 0x24, 0x25, 0x5e, 0x26, 0x2a, 0x28, 0x29, 0x5f, 0x2b, 0x8, 0x9, 0x51, 0x57, 0x45, 0x52, 0x54, 0x5a, 0x55, 0x49, 0x4f, 0x50, 0x7b, 0x7d, 0xa, 0x0, 0x41, 0x53, 0x44, 0x46, 0x47, 0x48, 0x4a, 0x4b, 0x4c, 0x3a, 0x3f, 0x0, 0x0, 0x7c, 0x59, 0x58, 0x43, 0x56, 0x42, 0x4e, 0x4d, 0x3c, 0x3e, 0x3f, 0x0, 0x2a, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2d, 0x0, 0x0, 0x0, 0x2b, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0
]


ia32_ps2_shift = 0
ia32_ps2_extended = 0


def ia32_ps_handle_int(irq):
    global ia32_ps2_kbd_us, ia32_ps2_kbd_us_sh
    global ia32_ps2_shift, ia32_ps2_extended
    if (ia32_inb(0x64) & 0b1) == 0:
        return 0
    sc = ia32_inb(0x60)

    # extended
    if sc == 0xE0:
        ia32_ps2_extended[0] = 1
        return 0

    if ia32_ps2_extended[0] != 0:
        ia32_ps2_extended[0] = 0
        return 0

    # key release
    if (sc & 0x80) != 0:
        sc = sc & 0x7F
        if sc == 42:  # left shift
            ia32_ps2_shift[0] = 0
        elif sc == 54:  # right shift
            ia32_ps2_shift[0] = 0
        return 0
    else:
        if sc == 42:  # left shift
            ia32_ps2_shift[0] = 1
            return 0
        elif sc == 54:  # right shift
            ia32_ps2_shift[0] = 1
            return 0

    # print("PS/2 interrupt: (c='")
    if sc < 128:
        if ia32_ps2_shift[0] == 1:
            char = ia32_ps2_kbd_us_sh[sc]
        else:
            char = ia32_ps2_kbd_us[sc]
        if char == 0:  # nothing
            return 0
        elif char == 27:  # escape
            return 0
        kputc(char)
    # print("', sc=")
    # print_n_hex(sc)
    # print(")\n")


@export
def ia32_ps2_init():
    global ia32_ps_handle_int
    ps2_wait_write()
    ia32_outb(0x64, 0xAD)  # disable first PS/2 port
    ps2_wait_write()
    ia32_outb(0x64, 0xA7)  # disable second PS/2 port

    # flush buffer
    while (ia32_inb(0x64) & 0b1) != 0:
        ia32_inb(0x60)

    ps2_wait_write()
    ia32_outb(0x64, 0x20)  # get configuration byte
    configbyte = ia32_inb(0x60)

    configbyte = (
        configbyte | 1 | (1 << 4) | (1 << 6)
    )  # first port: interrupt, clock, enable translation

    ps2_wait_write()
    ia32_outb(0x64, 0x60)  # set configuration byte
    ia32_outb(0x60, configbyte)

    ps2_wait_write()
    ia32_outb(0x64, 0xAE)  # enable first PS/2 port

    ia32_set_irq_handler(1, ia32_ps_handle_int)
    ia32_pic_unmask(1)
    print("initialized PS/2 controller\n")
