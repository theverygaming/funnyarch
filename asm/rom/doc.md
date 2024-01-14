# Funnyarch ROM

## Boot process

The ROM searches for a bootsector on the hard drive. It loads the first 512 bytes into memory and checks if the magic bytes `0x333A5252` (little endian) match up.
Then it jumps to the start of the sector + 4 (right after the magic bytes).
`r0` contains the start address of memory and `r1` contains the amount of memory available in bytes. This does not necessarily contain all system memory, another memory probe should be done.
`rsp` is set to zero and must be initialized by the bootsector.

## ROM calls (interrupts)

The ROM can be called into via interrupt 128

All rom functions may trash r0-r9 and system registers. They will not use the stack.

| r0 (function ID) | description                | return values                | r1                       | r2                              |
| ---------------- | -------------------------- | ---------------------------- | ------------------------ | ------------------------------- |
| 0                | read sector from disk      |                              | sector number            | pointer to 512-byte wide buffer |
| 1                | write character to serial  |                              | character in lowest byte |                                 |
| 2                | read character from serial | r0: character in lowest byte |                          |                                 |
| 3                | write string to serial     |                              | pointer to string        |                                 |

## Sample bootsector

```
// sample ROM bootsector
// magic bytes
.byte 0x52
.byte 0x52
.byte 0x3A
.byte 0x33
_entry:
// set up stack
add rsp, r0, r1
sub rsp, rsp, #4

mov r0, #3
mov r1, rip
add r1, rip, str_hello.rel
int #128

// disk read
mov r0, #0
mov r1, #1
mov r2, #0x2200
int #128


echoloop:
mov r0, #2
int #128
mov r1, r0
mov r0, #1
int #128
rjmp echoloop


str_hello:
.string "hello from bootsector!!!"
.align 4
```
