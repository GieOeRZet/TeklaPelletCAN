# P0 — FUN_0803E714 — BUILDER TABLICY PANELI — 2026-11-20

## Status

New hard trace from repository source. This pass attacks the OPEN question:
who writes `*(short *)(presenter + idx*2 + 0x20)` and where the gate for the graph-family entries is applied.

## HARD — direct source evidence

Function:

`FUN_0803E714` at runtime `0x0803E714`, Ghidra size 1040 B.

It initializes the panel-list count:

```c
*(undefined1 *)(param_1 + 0xe8) = 0;
```

It switches on:

```c
*(undefined1 *)(FUN_080314ba() + 299)
```

i.e. model/context offset `+0x12B`.

The function writes panel IDs directly into:

```c
param_1 + (uint)*(byte *)(param_1 + 0xe8) * 2 + 0x20
```

and increments `+0xE8`.

At the end it resolves every written ID with:

```c
FUN_08036ff2(*(undefined4 *)(param_1 + 8), (int)*psVar11)
```

and forwards the result to:

```c
FUN_0804842c(*(undefined4 *)(param_1 + 0x1c), uVar9 & 0xffff, uVar8)
```

Therefore `FUN_0803E714` is a real builder/producer of the runtime panel-ID list consumed later by `FUN_0803EC18`.

## HARD — access/config gates inside the builder

The same function repeatedly reads:

```c
FUN_080314ba() + 0x158
```

Examples:

- class 0..5 branches: additional list construction is conditional on `+0x158 != 0`;
- class 10:
  - base list of 5 entries is always added by `FUN_0803efda(param_1, DAT_0803eec0 + 0x48, 5)`;
  - if `+0x158 != 0`, another 0x13 entries are added;
  - if `+0x158 >= 2`, another 4 entries are added;
- class 1..4:
  - base 12 entries from `DAT_0803eec0 + 0x62`;
  - additional 11 entries when `+0x158 != 0`;
- class 0x10:
  - base 5 entries;
  - additional 0x13 entries when `+0x158 != 0`;
  - additional 2 entries when `+0x158 >= 2`.

## IMPORTANT — what this closes

The previous statement:

> the function filling `presenter + idx*2 + 0x20` is still unknown

is no longer correct.

It is now directly identified as:

`FUN_0803E714`

for the object/path represented by its `+0x12B` class dispatcher.

## STILL OPEN — exact Family-B graph gate

The remaining question is narrower:

> Does the 5-entry table at `DAT_0803EEC0 + 0x48` contain the panel key `0x48`, or does another branch produce `0x48`?

The code proves that class 10 receives five consecutive 16-bit IDs from:

`DAT_0803EEC0 + 0x48`

but the repository currently does not contain the runtime contents of the pointed RAM table.

Earlier raw-BIN evidence establishes:

`DAT_0803EEC0` contains pointers:

- `0x20011534`
- `0x20011650`
- `0x20011594`

Thus `DAT_0803EEC0 + 0x48` is a runtime RAM table location, not a static firmware table that can be decoded from the literal alone.

The exact five values must therefore be recovered from the binary/RAM initialization path.

## Related HARD mapping already known

From `FUN_0803EC18`:

- registry key `0x47` -> resolver indices `0x4A..0x4E` -> parameters `0x2261..0x2265`
- registry key `0x48` -> resolver indices `0x4F..0x53` -> parameters `0x2268,0x226E,0x226F,0x2275,0x227A`

The graph branch itself remains hard.

## Next exact search

1. Recover initialization/writes to RAM table `0x20011534`.
2. Specifically recover offsets `+0x48..+0x51` (five u16 values) used by class 10.
3. Trace whether one of those values is `0x48`.
4. If yes: class 10 is the producer/gate path for panel key `0x48`; determine the `+0x158` access-level/config relation.
5. If no: enumerate all other callers of `FUN_0803EFDA` and all direct writes to `param_1+0x20` for key `0x48`.

## Source

Full decompiled body preserved in:

`analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803e714-decompiled.c.txt`

