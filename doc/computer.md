# Memory Map

Everything above 0xF0000000 is generally MMIO

| address               | function                 |
| --------------------- | ------------------------ |
| 0xF0000000-0xF004B000 | 1bpp 640x480 framebuffer |
| 0xF004B000-0xF004B004 | Serial data register     |


# Serial

## Data register
Read -> RX buffer. Write -> TX buffer. High 3 bytes for status (no effect on write). Lowest byte is data
| bits | description                                               |
| ---- | --------------------------------------------------------- |
| 7:0  | Data                                                      |
| 8    | valid (not set when read was unsuccessful - buffer empty) |
| 31:9 | reserved                                                  |
