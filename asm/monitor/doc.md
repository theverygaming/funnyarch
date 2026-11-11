# funnyarch machine code monitor

_Note that each user input line has a limited length depending on how large the line buffer is_

_Only bold text in code blocks is user input_

## Reading memory

Examining a single address
<pre>
<b>A0</b>
000000A0: 84
</pre>

Examining multiple addresses
<pre>
<b>A0 A1 A2 A3 AF</b>
000000A0: 84
000000A1: D4
000000A2: 02
000000A3: 00
000000AF: 00
</pre>

Examining an address range
<pre>
<b>A0.AF</b>
000000A0: 84 D4 02 00 83 30 00 00
000000A8: 12 00 01 00 0B A0 00 00
</pre>

## Writing memory

_When writing a byte the previous value at the written location will be outputted_

Writing a single byte
<pre>
<b>10004A0:A0</b>
010004A0: 00
</pre>

Writing multiple bytes
<pre>
<b>10004A0:A0 A1 A2 A3 A4</b>
010004A0: 00
010004A1: 00
010004A2: 00
010004A3: 00
010004A4: 00
</pre>

## Jumping to an address

_Simply use the ``R`` suffix on the address to jump to_

For example to jump to address ``0x10004A0``
<pre>
<b>10004A0R</b>
</pre>

## Example usage

### Simple memory read & write

<pre>
<b>10004A0:A0 A1 A2 A3 A4 A5 A6</b>
010004A0: 00
010004A1: 00
010004A2: 00
010004A3: 00
010004A4: 00
010004A5: 00
010004A6: 00
</pre>

<pre>
<b>10004AF:AF</b>
010004AF: 00
</pre>

<pre>
<b>10004A0 10004AF</b>
010004A0: A0
010004AF: AF
</pre>

<pre>
<b>10004A0.10004AF</b>
010004A0: A0 A1 A2 A3 A4 A5 A6 00
010004A8: 00 00 00 00 00 00 00 AF
</pre>

## Example programs

### rjmp -1 (infinite loop)

<pre>
<b>10004A0: 03 FE FF FF</b>
010004A0: A0
010004A1: A1
010004A2: A2
010004A3: A3
</pre>

<pre>
<b>10004A0.10004A3</b>
010004A0: 03 FE FF FF
</pre>

<pre>
<b>10004A0R</b>
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
<b>10004A0:05 00 00 B0 05 40 04 F0</b>
<b>10004A8:05 02 48 00 08 02 00 00</b>
<b>10004B0:05 02 69 00 08 02 00 00</b>
<b>10004B8:05 02 21 00 08 02 00 00</b>
<b>10004C0:05 02 0A 00 08 02 00 00</b>
<b>10004C8:05 3C 00 00</b>
</pre>

<pre>
<b>10004A0.10004CB</b>
010004A0: 05 00 00 B0 05 40 04 F0
010004A8: 05 02 48 00 08 02 00 00
010004B0: 05 02 69 00 08 02 00 00
010004B8: 05 02 21 00 08 02 00 00
010004C0: 05 02 0A 00 08 02 00 00
010004C8: 05 3C 00 00
</pre>

<pre>
<b>10004A0R</b>
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
