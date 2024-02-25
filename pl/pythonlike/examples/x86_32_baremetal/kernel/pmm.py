pmm_ptr = 0
pmm_bn = 0
pmm_bs = 0
pmm_base = 0

def pmm_alloc_all():
    global pmm_ptr, pmm_bn
    word_n = (pmm_bn[0] / 8) / 4 # TODO: lang needs a way of knowing word size
    i = 0
    while i < word_n:
        pmm_ptr[i] = 0xFFFFFFFF # TODO: proper NOT in lang
        i = i + 1


# bstart = start block index
# bn = number of blocks to set
# alloc = wether to allocate or deallocate. 0 = deallocate 1 = allocate
@export
def pmm_set(bstart, bn, alloc):
    global pmm_ptr, pmm_bn
    if (bstart + bn) >= pmm_bn[0]:
        print_n_hex(bstart+bn)
        print("pmm: attempt to set out of range block\n")
        return 1
    alloc = alloc & 0b1
    while bn != 0:
        idx = bstart / (8*4)
        bidx = bstart % (8*4)
        pmm_ptr[idx] = (pmm_ptr[idx] & ((1 << bidx) ^ 0xFFFFFFFF)) | (alloc << bidx) # TODO: proper NOT in lang
        bstart = bstart + 1
        bn = bn - 1
    return 0


# ptr = pointer to start of bitmap, the bitmap size must be divisible by the word size and it must fit bn/8 bytes
# bn = number of blocks
# bs = block size in bytes, must be divisible by the word size
# base = base address of memory allocated by the bitmap
@export
def pmm_init(ptr, bn, bs, base):
    global pmm_ptr, pmm_bn, pmm_bs, pmm_base
    pmm_ptr[0] = ptr
    pmm_bn[0] = bn
    pmm_bs[0] = bs
    pmm_base[0] = base
    pmm_alloc_all()
    print("PMM initialized\n")


@export
def pmm_get_free_bytes():
    global pmm_ptr, pmm_bn, pmm_bs
    # TODO: lang needs a way of knowing word size
    free = 0
    word_n = (pmm_bn[0] / 8) / 4
    i = 0
    while i < word_n:
        bits = 0
        j = 0
        while j < 32: # TODO: lang needs a way of knowing word size
            bits = bits + ((pmm_ptr[i] >> j) & 0b1)
            j = j + 1
        free = free + (32 - bits) # TODO: lang needs a way of knowing word size
        i = i + 1
    return free * pmm_bs[0]


@export
def pmm_alloc_cont(bn):
    global pmm_ptr, pmm_bn, pmm_bs, pmm_base
    base = 0
    ncont = 0
    word_n = (pmm_bn[0] / 8) / 4 # TODO: lang needs a way of knowing word size
    i = 0
    while i < word_n:
        j = 0
        while j < 32: # TODO: lang needs a way of knowing word size
            used = (pmm_ptr[i] >> j) & 0b1
            if used == 0:
                if ncont == 0:
                    base = (i * 32) + j # TODO: lang needs a way of knowing word size
                ncont = ncont + 1
            else:
                base = 0
                ncont = 0
            if ncont == bn:
                break
            j = j + 1
        if ncont == bn:
            break
        i = i + 1
    if ncont == bn:
        pmm_set(base, bn, 1)
        return pmm_base[0] + (base * pmm_bs[0])
    panic("PMM out of memory")


@export
def pmm_free(addr, bn):
    global pmm_base, pmm_bs
    block = (addr - pmm_base[0]) / pmm_bs[0]
    pmm_set(block, bn, 0)
