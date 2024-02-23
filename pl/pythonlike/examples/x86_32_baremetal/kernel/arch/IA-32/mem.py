@export
def read_byte_unaligned(ptr):
    # return ptr[0] & 0xFF # if the architecture supports unaligned accesses
    misalignment_bits = (ptr & 0b11) << 3
    # TODO: lang needs a way of knowing word size
    ptr_aligned = ptr & 0xFFFFFFFC
    return (ptr_aligned[0] >> misalignment_bits) & 0xFF

@export
def write_byte_unaligned(ptr, data):
    misalignment_bits = (ptr & 0b11) << 3
    ptr_aligned = ptr & 0xFFFFFFFC
    data = (data & 0xFF) << misalignment_bits
    mask = (0xFF << misalignment_bits) ^ 0xFFFFFFFF # TODO: proper NOT in lang
    ptr_aligned[0] = (ptr_aligned[0] & mask) | data
