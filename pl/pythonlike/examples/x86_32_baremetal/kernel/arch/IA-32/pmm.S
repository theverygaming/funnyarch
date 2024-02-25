.section .bss
.global ia32_pmm_bitmap
.align 4
ia32_pmm_bitmap:
    // ((2^32)/4096)/8
    .fill 131072, 1, 0
