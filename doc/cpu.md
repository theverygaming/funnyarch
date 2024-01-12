# CPU

## Registers

| number | bits | name | description                     |
| ------ | ---- | ---- | ------------------------------- |
| 0      | 31:0 | r0   |                                 |
| 1      | 31:0 | r1   |                                 |
| 2      | 31:0 | r2   |                                 |
| 3      | 31:0 | r3   |                                 |
| 4      | 31:0 | r4   |                                 |
| 5      | 31:0 | r5   |                                 |
| 6      | 31:0 | r6   |                                 |
| 7      | 31:0 | r7   |                                 |
| 8      | 31:0 | r8   |                                 |
| 9      | 31:0 | r9   |                                 |
| 10     | 31:0 | r10  |                                 |
| 11     | 31:0 | r11  |                                 |
| 12     | 31:0 | r12  |                                 |
| 13     | 31:0 | r13  |                                 |
| 14     | 31:0 | r14  |                                 |
| 15     | 31:0 | r15  |                                 |
| 16     | 31:0 | r16  |                                 |
| 17     | 31:0 | r17  |                                 |
| 18     | 31:0 | r18  |                                 |
| 19     | 31:0 | r19  |                                 |
| 20     | 31:0 | r20  |                                 |
| 21     | 31:0 | r21  |                                 |
| 22     | 31:0 | r22  |                                 |
| 23     | 31:0 | r23  |                                 |
| 24     | 31:0 | r24  |                                 |
| 25     | 31:0 | r25  |                                 |
| 26     | 31:0 | r26  |                                 |
| 27     | 31:0 | rfp  | Frame pointer                   |
| 28     | 31:0 | lr   | Link register                   |
| 29     | 31:0 | rsp  | Stack pointer (grows downwards) |
| 30     | 31:0 | rip  | Instruction pointer             |
| 31     | 31:0 | rf   | CPU flags register              |

### rf (flags register)

| bits | description |
| ---- | ----------- |
| 0    | carry flag  |
| 1    | zero flag   |
| 31:2 | reserved    |

## System registers

| number | bits | name    | description                                                         |
| ------ | ---- | ------- | ------------------------------------------------------------------- |
| 0      | 31:0 | scr0    | Scratch register 0 (reserved for OS use in interrupt handlers etc.) |
| 1      | 31:0 | scr1    | Scratch register 1 (reserved for OS use in interrupt handlers etc.) |
| 2      | 31:0 | scr2    | Scratch register 2 (reserved for OS use in interrupt handlers etc.) |
| 3      | 31:0 | scr3    | Scratch register 3 (reserved for OS use in interrupt handlers etc.) |
| 4      | 31:0 | irip    | Previous `rip` on interrupt                                         |
| 5      | 31:0 | ibptr   | Base address of Interrupt Block                                     |
| 6      | 31:0 | pcst    | Processor state                                                     |
| 7      | 31:0 | tlbirip | Previous `rip` on TLB miss exception                                |
| 8      | 31:0 | tlbiptr | Physical address to jump to on TLB miss exception                   |
| 9      | 31:0 | tlbflt  | TLB refill address                                                  |


### pcst (Processor state register)

| bits  | description                        |
| ----- | ---------------------------------- |
| 0     | enable alignment exception         |
| 1     | enable usermode                    |
| 2     | enable TLB                         |
| 3     | enable hardware interrupts         |
| 4     | old enable alignment exception     |
| 5     | old enable usermode                |
| 6     | old enable TLB                     |
| 7     | old enable hardware interrupts     |
| 8     | old old enable alignment exception |
| 9     | old old enable usermode            |
| 10    | old old enable TLB                 |
| 11    | old old enable hardware interrupts |
| 23:12 | reserved                           |
| 31:24 | interrupt number                   |

The `pcst` system register contains a "stack" of state bits which makes an interrupt that causes a TLB miss possible.

## Interrupts / Exceptions

There are 256 different interrupt numbers.
On interrupt the CPU saves `rip` (pointing to the _next_ instruction in case of an interrupt and to the _current_ instruction in case of an exception) in `irip`, then the current state bits in `pcst` will be pushed to the state bit "stack", finally the interrupt number will be set in `pcst` and the usermode and enable hardware interrupts bits will be unset.
If the lowest bit of `ibptr` the CPU will now jump to the address in (`ibptr` & 0xFFFFFFFC).
If the bit is not set the CPU will jump to ((`ibptr` & 0xFFFFFFFC) + (4\*interrupt number)).

To return from an interrupt/exception use the `iret` instruction.

| number | type                        | description      |
| ------ | --------------------------- | ---------------- |
| 0-252  | Hardware/Software Interrupt |                  |
| 253    | Exception                   | Protection fault |
| 254    | Exception                   | Alignment fault  |
| 255    | Exception                   | Invalid opcode   |

## MMU

The CPU has a TLB which is populated by software. The page size is 4KiB.

When enabled each memory address accessed will be translated through the TLB. If an address that does not have a valid entry in the TLB is accessed a TLB miss exception will be thrown.

On TLB miss the CPU saves `rip` (pointing to the _current_ instruction) in `tlbirip`, then the current state bits in `pcst` will be pushed to the state bit "stack", then the usermode, enable hardware interrupts and enable TLB bits in `pcst` will be unset and finally the CPU will jump to (`tlbiptr` & 0xFFFFFFFC).

To return from a TLB miss exception use the `irettlb` instruction.

The TLB can be enabled by setting the "enable TLB" bit in the `pcst` system register.
Entires can be added with the `tlbw` instruction and invalidated with `invlpg`, the whole TLB can be invalidated with `invltlb`.

## Instruction encoding

All instructions are 32 bits in length. They can all be executed conditionally

### Condition codes

| value | name         | operation     | operation                                        |
| ----- | ------------ | ------------- | ------------------------------------------------ |
| 0     | always       | unconditional | always execute                                   |
| 1     | ifz/ifeq     | tgt == src    | execute if zero flag is set                      |
| 2     | ifnz/ifneq   | tgt != src    | execute if zero flag is not set                  |
| 3     | ifc/iflt     | tgt < src     | execute if carry flag is set                     |
| 4     | ifnc/ifgteq  | tgt >= src    | execute if carry flag is not set                 |
| 5     | ifnzc/ifgt   | tgt > src     | execute if both carry and zero flags are not set |
| 6     | ifzoc/iflteq | tgt <= src    | execute if zero flag or carry flag is set        |
| 7     | reserved     | reserved      | reserved                                         |

### E1

Assembler syntax: `cond instr tgt, src1, src2`

| bits  | description          |
| ----- | -------------------- |
| 5:0   | opcode               |
| 8:6   | condition            |
| 13:9  | source1              |
| 18:14 | source2              |
| 23:19 | target               |
| 31:24 | instruction-specific |

### E2

Assembler syntax: `cond instr tgt, src, imm13`

| bits  | description |
| ----- | ----------- |
| 5:0   | opcode      |
| 8:6   | condition   |
| 13:9  | source      |
| 18:14 | target      |
| 31:19 | imm13       |

### E3

Assembler syntax: `cond instr tgt, imm16`

| bits  | description          |
| ----- | -------------------- |
| 5:0   | opcode               |
| 8:6   | condition            |
| 13:9  | target               |
| 15:14 | instruction-specific |
| 31:16 | imm16                |

### E4

Assembler syntax: `cond instr imm23`

| bits | description |
| ---- | ----------- |
| 5:0  | opcode      |
| 8:6  | condition   |
| 31:9 | imm23       |

### E5

Assembler syntax: `cond instr tgt`

| bits  | description          |
| ----- | -------------------- |
| 5:0   | opcode               |
| 8:6   | condition            |
| 13:9  | target               |
| 31:14 | instruction-specific |

### E6

Assembler syntax: `cond instr`

| bits | description          |
| ---- | -------------------- |
| 5:0  | opcode               |
| 8:6  | condition            |
| 31:9 | instruction-specific |

### E7

Assembler syntax: `cond instr tgt, src`

| bits  | description          |
| ----- | -------------------- |
| 5:0   | opcode               |
| 8:6   | condition            |
| 13:9  | source               |
| 18:14 | target               |
| 31:19 | instruction-specific |

## instructions

| opcode | name    | encoding              | clock cycles | operation                                                                                                                                     | exceptions       |
| ------ | ------- | --------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| 0x00   | nop     | [E6](#e6)             | 3            | no operation                                                                                                                                  |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x01   | strpi   | [E2](#e2)             | 4            | target+=imm13 then mem[target]=source (imm13 is two's complement)                                                                             | alignment fault  |
| 0x02   | jmp     | [E4](#e4)             | 3            | jump to address in imm23<<2                                                                                                                   |                  |
| 0x03   | rjmp    | [E4](#e4)             | 3            | add imm23<<2 to rip (imm23 is two's complement)                                                                                               |                  |
| 0x04   | mov     | [E7](#e7)             | 3            | copy source register to destination register                                                                                                  |                  |
| 0x05   | mov     | [E3](#e3)             | 3            | target=imm16                                                                                                                                  |                  |
| 0x05   | movh    | [E3](#e3) [inst-sp=1] | 3            | target=(target & 0xFFFF) \| (imm16 << 16)                                                                                                     |                  |
| 0x06   | ldr     | [E2](#e2)             | 5            | target=mem[source+imm13] (imm13 is two's complement)                                                                                          | alignment fault  |
| 0x07   | ldri    | [E2](#e2)             | 5            | target=mem[source] then source+=imm13 (imm13 is two's complement)                                                                             | alignment fault  |
| 0x08   | str     | [E2](#e2)             | 4            | mem[target+imm13]=source (imm13 is two's complement)                                                                                          | alignment fault  |
| 0x09   | stri    | [E2](#e2)             | 4            | mem[target]=source then target+=imm13 (imm13 is two's complement)                                                                             | alignment fault  |
| 0x0a   | jal     | [E4](#e4)             | 3            | jump to address in imm23<<2 and store pointer to next instr in lr                                                                             |                  |
| 0x0b   | rjal    | [E4](#e4)             | 3            | add imm23<<2 to rip (imm23 is two's complement) and store pointer to next instr in lr                                                         |                  |
| 0x0c   | cmp     | [E7](#e7)             | 4            | perform operation target-source and update flags accordingly                                                                                  |                  |
| 0x0d   | cmp     | [E3](#e3)             | 4            | perform operation target-imm16 and update flags accordingly                                                                                   |                  |
| 0x0e   | int     | [E4](#e4)             | 3 (+4)       | software interrupt                                                                                                                            |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x10   | add     | [E1](#e1)             | 4            | target = source1 + source2                                                                                                                    |                  |
| 0x11   | add     | [E2](#e2)             | 4            | target = source + imm13                                                                                                                       |                  |
| 0x12   | add     | [E3](#e3)             | 4            | target = target + imm16                                                                                                                       |                  |
| 0x12   | addh    | [E3](#e3) [inst-sp=1] | 4            | target = target + (imm16 << 16)                                                                                                               |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x13   | sub     | [E1](#e1)             | 4            | target = source1 - source2                                                                                                                    |                  |
| 0x14   | sub     | [E2](#e2)             | 4            | target = source - imm13                                                                                                                       |                  |
| 0x15   | sub     | [E3](#e3)             | 4            | target = target - imm16                                                                                                                       |                  |
| 0x15   | subh    | [E3](#e3) [inst-sp=1] | 4            | target = target - (imm16 << 16)                                                                                                               |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x16   | shl     | [E1](#e1)             | 4            | target = source1 << source2                                                                                                                   |                  |
| 0x17   | shl     | [E2](#e2)             | 4            | target = source << imm13                                                                                                                      |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x18   | shr     | [E1](#e1)             | 4            | target = source1 >> source2                                                                                                                   |                  |
| 0x19   | shr     | [E2](#e2)             | 4            | target = source >> imm13                                                                                                                      |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x1A   | sar     | [E1](#e1)             | 4            | target = source1 >>> source2                                                                                                                  |                  |
| 0x1B   | sar     | [E2](#e2)             | 4            | target = source >>> imm13                                                                                                                     |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x1C   | and     | [E1](#e1)             | 4            | target = source1 & source2                                                                                                                    |                  |
| 0x1D   | and     | [E2](#e2)             | 4            | target = source & imm13                                                                                                                       |                  |
| 0x1E   | and     | [E3](#e3)             | 4            | target = target & imm16                                                                                                                       |                  |
| 0x1E   | andh    | [E3](#e3) [inst-sp=1] | 4            | target = target & (imm16 << 16)                                                                                                               |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x1F   | or      | [E1](#e1)             | 4            | target = source1 \| source2                                                                                                                   |                  |
| 0x20   | or      | [E2](#e2)             | 4            | target = source \| imm13                                                                                                                      |                  |
| 0x21   | or      | [E3](#e3)             | 4            | target = target \| imm16                                                                                                                      |                  |
| 0x21   | orh     | [E3](#e3) [inst-sp=1] | 4            | target = target \| (imm16 << 16)                                                                                                              |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x22   | xor     | [E1](#e1)             | 4            | target = source1 ^ source2                                                                                                                    |                  |
| 0x23   | xor     | [E2](#e2)             | 4            | target = source ^ imm13                                                                                                                       |                  |
| 0x24   | xor     | [E3](#e3)             | 4            | target = target ^ imm16                                                                                                                       |                  |
| 0x24   | xorh    | [E3](#e3) [inst-sp=1] | 4            | target = target ^ (imm16 << 16)                                                                                                               |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x25   | not     | [E7](#e7)             | 4            | target = ~source                                                                                                                              |                  |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x26   | mtsr    | [E7](#e7)             | ?            | copy source register to system register \| sysregs[target] = source                                                                           | Protection fault |
| 0x26   | mfsr    | [E7](#e7) [inst-sp=1] | ?            | copy system register to target register \| target = sysregs[source]                                                                           | Protection fault |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x27   | invlpg  | [E5](#e5)             | ?            | invalidate TLB entry that matches virtual address in target                                                                                   | Protection fault |
| 0x27   | invltlb | [E5](#e5) [inst-sp=1] | ?            | invalidate the entire TLB, the target register does not have any effect                                                                       | Protection fault |
| 0x28   | tlbw    | [E1](#e1)             | ?            | target -> physcal address (ignoring lower 12 bits), source1 -> virtual address (ignoring lower 12 bits), source2 -> flags (currently ignored) | Protection fault |
|        |         |                       |              |                                                                                                                                               |                  |
| 0x29   | iret    | [E6](#e6)             | ?            | Interrupt return                                                                                                                              | Protection fault |
| 0x29   | irettlb | [E6](#e6) [inst-sp=1] | ?            | TLB miss exception return                                                                                                                     | Protection fault |
