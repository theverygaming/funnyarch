# ia32_idt_arr defined in int_asm.S

ia32_idtr_arr = [
    2047, # 256*8-1 # 16-bit limit (sizeof idt -1) and first 16 bits of base pointer
    0, # high 16 bits of base and 16 bits of nothing
]

@export
def ia32_idt_init():
    global ia32_idt_arr, ia32_idtr_arr
    ia32_idtr_arr[0] = ia32_idtr_arr[0] | ((ia32_idt_arr & 0xFFFF) << 16)
    ia32_idtr_arr[1] = ia32_idt_arr >> 16
    i = 0
    while i < 256:
        ptr = ia32_idt_arr[i*2]
        # CS 8
        ia32_idt_arr[i*2] = (ptr & 0xFFFF) | (8 << 16)
        # interrupt gate, ring 0 only, present
        ia32_idt_arr[(i*2)+1] = (ptr & 0xFFFF0000) | (1 << 15) | (0b1110 << 8)
        i = i + 1
    ia32_idt_load(ia32_idtr_arr)
    print("loaded IDT\n")
