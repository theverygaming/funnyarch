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
<b>4A0:A0</b>
000004A0: 00
</pre>

Writing multiple bytes
<pre>
<b>4A0:A0 A1 A2 A3 A4</b>
000004A0: A0
000004A1: 00
000004A2: 00
000004A3: 00
000004A4: 00
</pre>

## Jumping to an address

_Simply use the ``R`` suffix on the address to jump to_

For example to jump to address ``0x4A0``
<pre>
<b>4A0R</b>
</pre>

## Example usage

### Simple memory read & write

<pre>
<b>4A0:A0 A1 A2 A3 A4 A5 A6</b>
000004A0: 00
000004A1: 00
000004A2: 00
000004A3: 00
000004A4: 00
000004A5: 00
000004A6: 00
</pre>

<pre>
<b>4AF:AF</b>
000004AF: 00
</pre>

<pre>
<b>4A0 4AF</b>
000004A0: A0
000004AF: AF
</pre>

<pre>
<b>4A0.4AF</b>
000004A0: A0 A1 A2 A3 A4 A5 A6 00
000004A8: 00 00 00 00 00 00 00 AF
</pre>

## Example programs

### rjmp -1 (infinite loop)

<pre>
<b>4A0: 03 FE FF FF</b>
000004A0: 03
000004A1: 00
000004A2: 00
000004A3: 00
</pre>

<pre>
<b>4A0.4A3</b>
000004A0: 03 FE FF FF
</pre>

<pre>
<b>4A0R</b>
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

<pre>
<b>4A0:05 00 00 B0 05 40 04 F0</b>
000004A0: 00
000004A1: 00
000004A2: 00
000004A3: 00
000004A4: 00
000004A5: 00
000004A6: 00
000004A7: 00
<b>4A8:05 02 48 00 08 02 00 00</b>
000004A8: 00
000004A9: 00
000004AA: 00
000004AB: 00
000004AC: 00
000004AD: 00
000004AE: 00
000004AF: 00
<b>4B0:05 02 69 00 08 02 00 00</b>
000004B0: 00
000004B1: 00
000004B2: 00
000004B3: 00
000004B4: 00
000004B5: 00
000004B6: 00
000004B7: 00
<b>4B8:05 02 21 00 08 02 00 00</b>
000004B8: 00
000004B9: 00
000004BA: 00
000004BB: 00
000004BC: 00
000004BD: 00
000004BE: 00
000004BF: 00
<b>4C0:05 02 0A 00 08 02 00 00</b>
000004C0: 00
000004C1: 00
000004C2: 00
000004C3: 00
000004C4: 00
000004C5: 00
000004C6: 00
000004C7: 00
<b>4C8:05 3C 00 00</b>
000004C8: 00
000004C9: 00
000004CA: 00
000004CB: 00
</pre>

<pre>
<b>4A0.4CB</b>
000004A0: 05 00 00 B0 05 40 04 F0
000004A8: 05 02 48 00 08 02 00 00
000004B0: 05 02 69 00 08 02 00 00
000004B8: 05 02 21 00 08 02 00 00
000004C0: 05 02 0A 00 08 02 00 00
000004C8: 05 3C 00 00
</pre>

<pre>
<b>4A0R</b>
Hi!
\
</pre>
