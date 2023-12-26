# funnyarch machine code monitor

_Note that each user input line has a limited length depending on how large the line buffer is_

_Only bold text in code blocks is user input_

## Reading memory

Examining a single address
<pre>
<b>A0</b>
000000A0: 0C
</pre>

Examining multiple addresses
<pre>
<b>A0 A1 A2 A3 AF</b>
000000A0: 0C
000000A1: 06
000000A2: 00
000000A3: 00
000000AF: FF
</pre>

Examining an address range
<pre>
<b>A0.AF</b>
000000A0: 0C 06 00 00 43 16 00 00
000000A8: 01 40 E7 FF 01 42 E7 FF
</pre>

## Writing memory

_When writing a byte the previous value at the written location will be outputted_

Writing a single byte
<pre>
<b>24A0:A0</b>
000024A0: 00
</pre>

Writing multiple bytes
<pre>
<b>24A0:A0 A1 A2 A3 A4</b>
000024A0: 00
000024A1: 00
000024A2: 00
000024A3: 00
000024A4: 00
</pre>

## Jumping to an address

_Simply use the ``R`` suffix on the address to jump to_

For example to jump to address ``0x24A0``
<pre>
<b>24A0R</b>
</pre>

## Example usage

### Simple memory read & write

<pre>
<b>24A0:A0 A1 A2 A3 A4 A5 A6</b>
000024A0: 00
000024A1: 00
000024A2: 00
000024A3: 00
000024A4: 00
000024A5: 00
000024A6: 00
</pre>

<pre>
<b>24AF:AF</b>
000024AF: 00
</pre>

<pre>
<b>24A0 24AF</b>
000024A0: A0
000024AF: AF
</pre>

<pre>
<b>24A0.24AF</b>
000024A0: A0 A1 A2 A3 A4 A5 A6 00
000024A8: 00 00 00 00 00 00 00 AF
</pre>

## Example programs

### rjmp -1 (infinite loop)

<pre>
<b>24A0: 03 FE FF FF</b>
000024A0: A0
000024A1: A1
000024A2: A2
000024A3: A3
</pre>

<pre>
<b>24A0.24A3</b>
000024A0: 03 FE FF FF
</pre>

<pre>
<b>24A0R</b>
</pre>
_infinite loop_

### Serial "Hi!"

<pre>
// Serial data register
mov r0, #0xB000
movh r0, #0xF004

mov r1, #0x48 // 'H'
str r0, r1, #0
mov r1, #0x69 // 'i'
str r0, r1, #0
mov r1, #0x21 // '!'
str r0, r1, #0
mov r1, #0x0A // '\n'
str r0, r1, #0

mov rip, #0
</pre>

_Obviously expect output inbetween these lines.._
<pre>
<b>24A0:05 00 00 B0 05 40 04 F0</b>
<b>24A8:05 02 48 00 08 02 00 00</b>
<b>24B0:05 02 69 00 08 02 00 00</b>
<b>24B8:05 02 21 00 08 02 00 00</b>
<b>24C0:05 02 0A 00 08 02 00 00</b>
<b>24C8:05 3C 00 00</b>
</pre>

<pre>
<b>24A0.24CB</b>
000024A0: 05 00 00 B0 05 40 04 F0
000024A8: 05 02 48 00 08 02 00 00
000024B0: 05 02 69 00 08 02 00 00
000024B8: 05 02 21 00 08 02 00 00
000024C0: 05 02 0A 00 08 02 00 00
000024C8: 05 3C 00 00
</pre>

<pre>
<b>24A0R</b>
Hi!
\
</pre>

### Write to the framebuffer

_Not a program but.._

_Obviously expect output inbetween these lines.._

<pre>
<b>F0000000:1C 1C 1C 1C 1C 1C 1C 1C 1C</b>
<b>F0000050:11 11 11 11 11 11 11 11 11</b>
<b>F00000A0:18 18 18 18 18 18 18 18 18</b>
<b>F00000F0:11 11 11 11 11 11 11 11 11</b>
<b>F0000140:1C 1C 1C 1C 1C 1C 1C 1C 1C</b>
</pre>
