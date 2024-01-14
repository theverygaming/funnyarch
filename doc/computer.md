# Memory Map

Everything above 0xF0000000 is generally MMIO

| address               | function                               |
| --------------------- | -------------------------------------- |
| 0xF0000000-0xF004B000 | 1bpp 640x480 framebuffer               |
| 0xF004B000-0xF004B004 | Serial data register                   |
| 0xF004B004-0xF004B008 | HDD control/status register            |
| 0xF004B008-0xF004B00C | HDD info register                      |
| 0xF004B00C-0xF004B010 | HDD controller control/status register |
| 0xF004B010-0xF004B210 | HDD data buffer                        |


# Serial

## Data register
Read -> RX buffer. Write -> TX buffer. High 3 bytes for status (no effect on write). Lowest byte is data
| bits | description                                               |
| ---- | --------------------------------------------------------- |
| 7:0  | Data                                                      |
| 8    | valid (not set when read was unsuccessful - buffer empty) |
| 31:9 | reserved                                                  |

# HDD

## Control/Status register

| bits | description                                                |
| ---- | ---------------------------------------------------------- |
| 1:0  | operation - 0 = none, 1 = read, 2 = write                  |
| 2    | set when operation finished (never set for none operation) |
| 31:3 | Sector index                                               |

## Info register

| bits  | description                |
| ----- | -------------------------- |
| 28:0  | Number of sectors on drive |
| 31:29 | Reserved                   |

## Controller control/status register

| bits | description |
| ---- | ----------- |
| 31:0 | Reserved    |

## Data buffer

HDD Read/Write data buffer. 512 bytes in size

## Interrupts

The HDD controller would send an interrupt when it finishes an operation (read/write).
_This functionality isn't implemented anywhere yet though, so for now polling is needed_
