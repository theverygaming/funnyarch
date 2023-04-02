## Registers

All registers are 64 bits wide.
- **r0-r31**: general purpose
- **rip**(r32): instruction pointer - when accessed contains a pointer to the beginning of the _next_ instruction
- **rsp**(r33): stack pointer
- **rflags**(r34): various CPU state flags (carry etc.)
- **risp**(r35): interrupt stack pointer (supervisor only)
- **rsflags**(r36): supervisor flags (interrupt enable etc.) (supervisor only)
- **rivt**(r37): pointer to interrupt vector table (supervisor only)
- **rpd**(r38): pointer to page directory (supervisor only)


### flags
| bits | name  | description |
|------|-------|-------------|
| 0    | carry | carry flag  |
| 1    | zero  | zero flag   |

### sflags
| bits | name       | description                  |
|------|------------|------------------------------|
| 0    | interrupt  | enable hardware interrupts   |
| 1    | supervisor | if CPU is in supervisor mode |
| 2    | mmu        | if MMU is enabled            |


## Instructions

### Encondig

#### control
| bits  | name   | description                      |
|-------|--------|----------------------------------|
| 6:0   | opcode | operation code                   |
| 8:7   | size   | operation size (8/16/32/64 bits) |
| 10:9  | source | source operand type              |
| 12:11 | target | target operand type              |
| 15:13 | cond   | condition code                   |

control comes first, then source and target operands follow


### Opcodes

| value | name   | operands | op sizes   | description                             | privilege level |
|-------|--------|----------|------------|-----------------------------------------|-----------------|
| 0x00  | UD     | none     | 8/16/32/64 | undefined instruction                   | /               |
| 0x01  | NOP    | none     | 8/16/32/64 | no operation                            | user            |
| 0x02  | MOV    | src+tgt  | 8/16/32/64 | move (zero extend by default)           | user            |
| 0x03  | ADD    | src+tgt  | 8/16/32/64 | add                                     | user            |
| 0x04  | SUB    | src+tgt  | 8/16/32/64 | subtract                                | user            |
| 0x05  | DIV    | src+tgt  | 8/16/32/64 | divide (unsigned)                       | user            |
| 0x06  | IDIV   | src+tgt  | 8/16/32/64 | divide (signed)                         | user            |
| 0x07  | MUL    | src+tgt  | 8/16/32/64 | multiply (unsigned)                     | user            |
| 0x08  | IMUL   | src+tgt  | 8/16/32/64 | multiply (signed)                       | user            |
| 0x09  | REM    | src+tgt  | 8/16/32/64 | remainder (unsigned)                    | user            |
| 0x0A  | IREM   | src+tgt  | 8/16/32/64 | remainder (signed)                      | user            |
| 0x0B  | SHR    | src+tgt  | 8/16/32/64 | logical shift right (zero extension)    | user            |
| 0x0C  | SHL    | src+tgt  | 8/16/32/64 | logical shift left                      | user            |
| 0x0D  | SAR    | src+tgt  | 8/16/32/64 | arithmetic shift right (sign extension) | user            |
| 0x0E  | AND    | src+tgt  | 8/16/32/64 | bitwise AND                             | user            |
| 0x0F  | OR     | src+tgt  | 8/16/32/64 | bitwise OR                              | user            |
| 0x10  | XOR    | src+tgt  | 8/16/32/64 | bitwise XOR                             | user            |
| 0x11  | NOT    | src+tgt  | 8/16/32/64 | bitwise NOT                             | user            |
| 0x12  | TEST   | src+tgt  | 8/16/32/64 | test if bit set                         | user            |
| 0x13  | JMP    | src      | 64         | absolute jump                           | user            |
| 0x14  | RJMP   | src      | 64         | relative jump                           | user            |
| 0x15  | CMP    | src+tgt  | 8/16/32/64 | compare                                 | user            |
| 0x16  | INT    | src      | 8          | software interrupt                      | user            |
| 0x17  | IRET   | none     | 8/16/32/64 | return from interrupt                   | supervisor      |
| 0x18  | WFI    | none     | 8/16/32/64 | wait for interrupt                      | supervisor      |
| 0x19  | INVLPG | src      | 64         | flush TLB entry                         | supervisor      |


### Operation sizes

| value | description |
|-------|-------------|
| 0     | 8 bits      |
| 1     | 16 bits     |
| 2     | 32 bits     |
| 3     | 64 bits     |


### Operand types

| value | description       | size of operand | what's actually stored?    |
|-------|-------------------|-----------------|----------------------------|
| 0     | register          | 8 bits          | register number            |
| 1     | register pointer  | 8 bits          | register number            |
| 2     | immediate         | operation size  | value                      |
| 3     | immediate pointer | 64 bits         | pointer to memory location |


### Condition codes

| value | name   | description                                        |
|-------|--------|----------------------------------------------------|
| 0     | always | execute unconditionally                            |
| 1     | ifz    | execute if zero flag is set                        |
| 2     | ifnz   | execute if zero flag is not set                    |
| 3     | ifc    | execute if carry flag is set                       |
| 4     | ifnc   | execute if carry flag is not set                   |
| 5     | ifnzc  | execute if neither zero flag nor carry flag is set |
| 6     | ifzoc  | execute if zero flag or carry flag is set          |


## Exceptions/Interrupts

There are 256 interrupt/exception vectors. When an interrupt or exception occours the CPU will access a table pointed to by the ivt register. This table simply contains 256 64-bit wide pointers to the interrupt handlers. Every single one of these pointers must point to a valid handler (There may be a single handler for all of them).

Hardware interrupts can be disabled by clearing the interrupt bit in the flags register. Software interrupts and exceptions on the other hand cannot be disabled.

If an Exception occours while trying to call an interrupt/exception handler the CPU will reset.

Exceptions:
| vector | description                        |
|--------|------------------------------------|
| 0x0    | page fault (pushes special values) |
| 0x1    | protection fault                   |
| 0x2    | invalid opcode                     |
| 0x3    | divide by zero                     |

On interrupt/exception the CPU will:
- swap **isp** to **sp**
- push the old **sp**
- push **ip**
- push **flags**
- push **sflags**
- push interrupt vector (8 bit)
- clear interrupt flag in **sflags**
- *on page fault the CPU will push*
  - address page fault occoured at (64 bit)
  - page fault info (8 bit)

### page fault info
| bits | name              | description                                      |
|------|-------------------|--------------------------------------------------|
| 0    | read              | on read operation                                |
| 1    | write             | on write operation                               |
| 2    | instruction fetch | on instruction fetch                             |
| 3    | not present       | page not present                                 |
| 4    | supervisor        | tried to access a supervisor page from user mode |

The `iret` instruction will:
- pop **sflags**
- pop **flags**
- pop **ip**
- pop **sp**
