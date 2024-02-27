@export
def ia32_init(magic, mb2info):
    global ia32_pmm_bitmap
    ia32_printk_init()
    ia32_gdt_init()
    ia32_idt_init()
    ia32_pic_init()
    ia32_ps2_init()
    pmm_init(
        ia32_pmm_bitmap, 1048576, 4096, 0
    )  # number of pages in 4GiB, page size, start at address 0
    if magic == 0x36D76289:
        print("booted by multiboot2\n")
        ia32_multiboot2_read_memmap(mb2info)
        ia32_multiboot2_read_module(mb2info)
    kinit()
    while 1 == 1:
        pass
