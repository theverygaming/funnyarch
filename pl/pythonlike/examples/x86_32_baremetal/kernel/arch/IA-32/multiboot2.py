def memmap_set(bl, bh, ll, lh, allocate):
    if lh != 0:
        ll = 0xFFFFFFFF - bl
    if bh != 0:
        if bl == 0:
            ll = 0
        else:
            ll = 0xFFFFFFFF - bl
    if allocate == 0:
        # align base address up
        bl = (bl + 4095) & (4095 ^ 0xFFFFFFFF)  # TODO: proper NOT in lang
        # align length down
        ll = ll & (4095 ^ 0xFFFFFFFF)  # TODO: proper NOT in lang
    else:
        # align base address down
        bl = bl & (4095 ^ 0xFFFFFFFF)  # TODO: proper NOT in lang
        # align length up
        ll = (ll + 4095) & (4095 ^ 0xFFFFFFFF)  # TODO: proper NOT in lang
    if (bl + ll) < bl:
        ll = 0xFFFFFFFF - bl
    pmm_set(bl / 4096, ll / 4096, allocate)


def multiboot_find_tag(mb2info, t):
    mbisize = mb2info[0]
    tag = mb2info + 8
    while tag[0] != 0:  # tag->type != 0
        tag_type = tag[0]  # tag->type
        tag_size = tag[1]  # tag->size
        if tag_type == t:  # tag->type == t
            return tag
        tag = tag + (
            (tag_size + 7) & (7 ^ 0xFFFFFFFF)
        )  # tag += ((tag->size + 7) & ~7) # TODO: proper NOT in lang
    return 0


@export
def ia32_multiboot2_read_memmap(mb2info):
    tag = multiboot_find_tag(mb2info, 6)  # MULTIBOOT_TAG_TYPE_MMAP
    if tag == 0:
        return 0
    tag_size = tag[1]  # tag->size
    entry_size = tag[2]
    n_entries = tag_size / entry_size
    # print("  mb2 memmap(entry_size=")
    # print_n_hex(entry_size)
    # print(", n_entries=")
    # print_n_hex(n_entries)
    # print(")\n")
    # entry_ptr = tag + 16
    # i = 0
    # while i < n_entries:
    #    b_low = entry_ptr[0]
    #    b_hi = entry_ptr[1]
    #    l_low = entry_ptr[2]
    #    l_hi = entry_ptr[3]
    #    t = entry_ptr[4]
    #    print("    (bl=")
    #    print_n_hex(b_low)
    #    print(", bh=")
    #    print_n_hex(b_hi)
    #    print(", ll=")
    #    print_n_hex(l_low)
    #    print(", lh=")
    #    print_n_hex(l_hi)
    #    print(", t=")
    #    print_n_hex(t)
    #    print(")\n")
    #    entry_ptr = entry_ptr + entry_size
    #    i = i + 1
    entry_ptr = tag + 16
    i = 0
    while i < n_entries:
        b_low = entry_ptr[0]
        b_hi = entry_ptr[1]
        l_low = entry_ptr[2]
        l_hi = entry_ptr[3]
        t = entry_ptr[4]
        if t == 1:
            memmap_set(b_low, b_hi, l_low, l_hi, 0)
        entry_ptr = entry_ptr + entry_size
        i = i + 1
    entry_ptr = tag + 16
    i = 0
    while i < n_entries:
        b_low = entry_ptr[0]
        b_hi = entry_ptr[1]
        l_low = entry_ptr[2]
        l_hi = entry_ptr[3]
        t = entry_ptr[4]
        if t != 1:
            memmap_set(b_low, b_hi, l_low, l_hi, 1)
        entry_ptr = entry_ptr + entry_size
        i = i + 1


@export
def ia32_multiboot2_read_module(mb2info):
    tag = multiboot_find_tag(mb2info, 3)  # MULTIBOOT_TAG_TYPE_MODULE
    if tag == 0:
        return 0
    mod_start = tag[2]
    mod_end = tag[3]
    print("  mb2 module (start=")
    print_n_hex(mod_start)
    print(", end=")
    print_n_hex(mod_end)
    print(")\n")
    res_st = mod_start
    res_len = mod_end - mod_start
    # align base address down
    res_st = res_st & (4095 ^ 0xFFFFFFFF)  # TODO: proper NOT in lang
    # align length up
    res_len = (res_len + 4095) & (4095 ^ 0xFFFFFFFF)  # TODO: proper NOT in lang
    pmm_set(res_st / 4096, res_len / 4096, 1)
