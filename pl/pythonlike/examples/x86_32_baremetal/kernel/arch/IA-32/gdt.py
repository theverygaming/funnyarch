ia32_gdt_arr = [
    0, # null
    0, # null
    0x0000ffff, # code
    0x00cf9a00, # code
    0x0000ffff, # data
    0x00cf9200, # data
]

ia32_gdtr_arr = [
    23, # 16-bit limit (sizeof gdt -1) and first 16 bits of base pointer
    0, # high 16 bits of base and 16 bits of nothing
]

@export
def ia32_gdt_init():
    global ia32_gdt_arr, ia32_gdtr_arr
    ia32_gdtr_arr[0] = ia32_gdtr_arr[0] | ((ia32_gdt_arr & 0xFFFF) << 16)
    ia32_gdtr_arr[1] = ia32_gdt_arr >> 16
    ia32_gdt_load(ia32_gdtr_arr, 8, 16)
    print("loaded GDT\n")
