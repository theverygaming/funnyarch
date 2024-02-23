@export
def ia32_init(magic, mb2info):
    if magic == 0x36d76289:
        print("booted by multiboot2\n")
    kinit()
    while 1 == 1:
        pass
