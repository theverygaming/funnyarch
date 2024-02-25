@export
def ia32_pic_check_spurious():
    # TODO: check if it was spurious
    return 0

@export
def ia32_pic_eoi(irq):
    if irq >= 8:
        ia32_outb(0xA0, 0x20) # PIC2: EOI
    ia32_outb(0x20, 0x20) # PIC1: EOI

@export
def ia32_pic_mask(irq):
    if irq >= 8:
        reg =  0xA1 # PIC2: mask
        irq = irq - 8
    else:
        reg = 0x21 # PIC1: mask
    mask = ia32_inb(reg)
    mask = mask | (1 << irq)
    ia32_outb(reg, mask)

@export
def ia32_pic_unmask(irq):
    if irq >= 8:
        reg =  0xA1 # PIC2: mask
        irq = irq - 8
    else:
        reg = 0x21 # PIC1: mask
    mask = ia32_inb(reg)
    mask = mask & ((1 << irq) ^ 0xFFFFFFFF) # TODO: proper NOT in lang
    ia32_outb(reg, mask)

@export
def ia32_pic_init():
    ia32_outb(0x20, 0x11) # PIC1: init
    ia32_io_wait()
    ia32_outb(0xA0, 0x11) # PIC2: init
    ia32_io_wait()
    ia32_outb(0x21, 32) # PIC1: offset
    ia32_io_wait()
    ia32_outb(0xA1, 40) # PIC2: offset
    ia32_io_wait()
    ia32_outb(0x21, 0x04) # PIC1: PIC2 @IRQ2
    ia32_io_wait()
    ia32_outb(0xA1, 0x02) # PIC2: cascade identity 2
    ia32_io_wait()
    ia32_outb(0x21, 0x01) # PIC1: 8086 mode
    ia32_io_wait()
    ia32_outb(0xA1, 0x01) # PIC2: 8086 mode
    ia32_io_wait()

    ia32_outb(0x21, 0xFB) # PIC1: all masked (other than IRQ2 which is PIC2)
    ia32_outb(0xA1, 0xFF) # PIC2: all masked

    print("Initialized PIC\n")
    ia32_enable_interrupts()
    print("enabled interrupts\n")
