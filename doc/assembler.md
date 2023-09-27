# Assembler

## Macros

### How to define macros

You can define macros without arguments. They will be inserted on any word boundary (not inside a word)

```c
#define MOV mov
#define EXAMPLE MOV

ifz EXAMPLE r0, r1 // this works
// expands to
ifz mov r0, r1

ifzEXAMPLE r0, r1 // this doesn't work
// expands to
ifzEXAMPLE r0, r1
```

Multiline macros with arguments are also possible.

```c
#define MOV_AND_ADD(rega, regb) mov regb, rega \
                                add regb, rega

MOV_AND_ADD(r0, r1) // this works
// expands to
mov r1, r0
add r1, r0

ifz MOV_AND_ADD(r0, r1) // this doesn't work
// expands to
ifz MOV_AND_ADD(r0, r1)
```

### Builtin macros

#### `__builtin_push(register)`

`strpi rsp, register, #-4`

#### `__builtin_pop(register)`

`ldri register, rsp, #4`

#### `__builtin_call_lbl(label)`

`jal label`

#### `__builtin_relcall_lbl(label)`

`rjal label`

#### `__builtin_return`

`mov rip, lr`
