ENTRY(_start)

SECTIONS
{
    . = 1M;

    .entry : {
        *(.entry)
    }
    .text : {
        *(.text)
    }
    .data : {
        *(.data)
    }
    .rodata : {
        *(.rodata)
    }
    .bss : {
        *(.bss)
    }
}
