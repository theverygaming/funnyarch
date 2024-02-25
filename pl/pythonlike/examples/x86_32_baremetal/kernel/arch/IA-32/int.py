ia32_irq_handler_arr = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

@export
def ia32_handle_int(n, err):
    global ia32_irq_handler_arr
    if n < 32:
        print("exception!! (n=")
        print_n_hex(n)
        print(" e=")
        print_n_hex(err)
        print(")\n")
        panic("exception")
        while 1 == 1:
            pass
    #print("interrupt (n=")
    #print_n_hex(n)
    #print(")\n")

    # IRQ?
    if n < 48:
        if ia32_pic_check_spurious() != 0:
            #print("spurious interrupt\n")
            return 0
        irq = n-32
        if ia32_irq_handler_arr[irq] != 0:
            hndlr = ia32_irq_handler_arr[irq]
            hndlr(irq)

        ia32_pic_eoi(irq)

@export
def ia32_set_irq_handler(irq, handler):
    global ia32_irq_handler_arr
    if irq < 16:
        ia32_irq_handler_arr[irq] = handler
