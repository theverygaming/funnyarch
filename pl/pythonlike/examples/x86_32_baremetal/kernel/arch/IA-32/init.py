@export
def ia32_init(magic, mb2info):
    ia32_printk_init()
    ia32_gdt_init()
    ia32_idt_init()
    ia32_pic_init()
    ia32_ps2_init()
    if magic == 0x36d76289:
        print("booted by multiboot2\n")
    kinit()
    while 1 == 1:
        pass
