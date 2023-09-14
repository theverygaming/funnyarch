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
| 27     | 31:0 | r27  |                                 |
| 28     | 31:0 | lr   |                                 |
| 29     | 31:0 | rsp  | Stack pointer (grows downwards) |
| 30     | 31:0 | rip  | Instruction pointer             |
| 31     | 31:0 | rf   | CPU flags register              |

### rf (flags register)

| bits | description |
| ---- | ----------- |
| 0    | carry flag  |
| 1    | zero flag   |
| 31:2 | reserved    |

## Instruction encoding

All instructions are 32 bits in length. They can all be executed conditionally

### Condition codes

| value | name         | operation    | operation                                        |
| ----- | ------------ | ------------ | ------------------------------------------------ |
| 0     | always       | unconditinal | always execute                                   |
| 1     | ifz/ifeq     | tgt == src   | execute if zero flag is set                      |
| 2     | ifnz/ifneq   | tgt != src   | execute if zero flag is not set                  |
| 3     | ifc/iflt     | tgt < src    | execute if carry flag is set                     |
| 4     | ifnc/ifgteq  | tgt >= src   | execute if carry flag is not set                 |
| 5     | ifnzc/ifgt   | tgt > src    | execute if both carry and zero flags are not set |
| 6     | ifzoc/iflteq | tgt <= src   | execute if zero flag or carry flag is set        |

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

| opcode | name  | encoding  | clock cycles | operation                                                                             |
| ------ | ----- | --------- | ------------ | ------------------------------------------------------------------------------------- |
| 0x00   | nop   | [E6](#e6) | 2            | no operation                                                                          |
|        |       |           |              |                                                                                       |
| 0x01   | strpi | [E2](#e2) | 2            | target+=imm13 then mem[target]=source (imm13 is two's complement)                     |
| 0x02   | jmp   | [E4](#e4) | 2            | jump to address in imm23<<2                                                           |
| 0x03   | rjmp  | [E4](#e4) | 2            | add imm23<<2 to rip (imm23 is two's complement)                                       |
| 0x04   | mov   | [E7](#e7) | 2            | copy source register to destination register                                          |
| 0x05   | mov   | [E3](#e3) | 2            | target=imm16 - target=(target & 0xFF) \| (imm16<<16) if bit 14 set                    |
| 0x06   | ldr   | [E2](#e2) | 3            | target=mem[source+imm13] (imm13 is two's complement)                                  |
| 0x07   | ldri  | [E2](#e2) | 3            | target=mem[source] then source+=imm13 (imm13 is two's complement)                     |
| 0x08   | str   | [E2](#e2) | 2            | mem[target+imm13]=source (imm13 is two's complement)                                  |
| 0x09   | stri  | [E2](#e2) | 2            | mem[target]=source then target+=imm13 (imm13 is two's complement)                     |
| 0x0a   | jal   | [E4](#e4) | 2            | jump to address in imm23<<2 and store pointer to next instr in lr                     |
| 0x0b   | rjal  | [E4](#e4) | 2            | add imm23<<2 to rip (imm23 is two's complement) and store pointer to next instr in lr |
| 0x0c   | cmp   | [E7](#e7) | 3            | perform operation target-source and update flags accordingly                          |
| 0x0d   | cmp   | [E3](#e3) | 3            | perform operation imm16-target and update flags accordingly                           |
|        |       |           |              |                                                                                       |
| 0x10   | add   | [E1](#e1) | 3            | target = source1 + source2                                                            |
| 0x11   | add   | [E2](#e2) | 3            | target = source + imm13                                                               |
| 0x12   | add   | [E3](#e3) | 3            | target = target + imm16 - target = target + (imm16<<16) if bit 14 set                 |
|        |       |           |              |                                                                                       |
| 0x13   | sub   | [E1](#e1) | 3            | target = source1 - source2                                                            |
| 0x14   | sub   | [E2](#e2) | 3            | target = source - imm13                                                               |
| 0x15   | sub   | [E3](#e3) | 3            | target = target - imm16 - target = target - (imm16 << 16) if bit 14 set               |
|        |       |           |              |                                                                                       |
| 0x16   | shl   | [E1](#e1) | 3            | target = source1 << source2                                                           |
| 0x17   | shl   | [E2](#e2) | 3            | target = source << imm13                                                              |
|        |       |           |              |                                                                                       |
| 0x18   | shr   | [E1](#e1) | 3            | target = source1 >> source2                                                           |
| 0x19   | shr   | [E2](#e2) | 3            | target = source >> imm13                                                              |
|        |       |           |              |                                                                                       |
| 0x1A   | sar   | [E1](#e1) | 3            | target = source1 >>> source2                                                          |
| 0x1B   | sar   | [E2](#e2) | 3            | target = source >>> imm13                                                             |

<!-- TODO: fix this  -->

## pseudoinstructions

| opcode | name | encoding  | clock cycles | operation                                       |
| ------ | ---- | --------- | ------------ | ----------------------------------------------- |
| 0x00   | nop  | [E6](#e6) | 2            | no operation                                    |
|        |      |           |              |                                                 |
| 0x01   | jmp  | [E5](#e5) | 2            | jump to address in target                       |
| 0x02   | jmp  | [E4](#e4) | 2            | jump to address in imm23<<2                     |
| 0x03   | rjmp | [E4](#e4) | 2            | add imm23<<2 to rip (imm23 is two's complement) |
|        |      |           |              |                                                 |
| 0x10   | add  | [E1](#e1) | 3            | target=source1+source2                          |
| 0x11   | add  | [E2](#e2) | 3            | target=source+imm13                             |
| 0x12   | addl | [E3](#e3) | 3            | target=target+imm16                             |
| 0x12   | addh | [E3](#e3) | 3            | target=target+(imm16<<16)                       |
|        |      |           |              |                                                 |
| 0x13   | sub  | [E1](#e1) | 3            | target=source1-source2                          |
| 0x14   | sub  | [E2](#e2) | 3            | target=source-imm13                             |
| 0x15   | subl | [E3](#e3) | 3            | target=target-imm16                             |
| 0x15   | subh | [E3](#e3) | 3            | target=target-(imm16<<16)                       |
