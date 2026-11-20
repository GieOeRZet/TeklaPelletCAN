# MULTIPASS-21 — IAR INIT TABLE EXECUTION CHECKPOINT — 2026-11-20

## Scope

Execution-only checkpoint requested by the user for the external deep-analysis agent. This document records raw execution results; interpretation remains with the external agent.

Firmware:
- FW2213TK_kopia.bin
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
- Working runtime/file base used for this pass: 0x08010000.

## Task 1 — disassembly 0x89440..0x89490

Raw disassembly:

```asm
89440: b510          push    {r4, lr}
89442: 4907          ldr     r1, [pc, #0x1c]
89444: 4479          add     r1, pc
89446: 3118          adds    r1, #0x18
89448: 4c06          ldr     r4, [pc, #0x18]
8944a: 447c          add     r4, pc
8944c: 3416          adds    r4, #0x16
8944e: e004          b       0x8945a
89450: 680a          ldr     r2, [r1]
89452: 1d08          adds    r0, r1, #0x4
89454: 4411          add     r1, r2
89456: 4788          blx     r1
89458: 4601          mov     r1, r0
8945a: 42a1          cmp     r1, r4
8945c: d1f8          bne     0x89450
8945e: bd10          pop     {r4, pc}

89460: 206c
89462: 0000
89464: 208c
89466: 0000
```

PC-relative literal-derived file offsets recorded during execution:
- table start: 0x08B4C8
- table limit: 0x08B4EE

## Task 2 — raw table dump

Raw bytes 0x08B4C8..0x08B4EE:

```
70 47 00 00 29 d0 fe ff c4 e9 00 00 28 5f 01 20
00 00 00 00 b1 31 fe ff 34 ac 00 00 74 10 00 00
00 00 00 20 61 0c 00 00
```

32-bit little-endian words:

```
08B4C8: 0x00004770
08B4CC: 0xFFFED029
08B4D0: 0x0000E9C4
08B4D4: 0x20015F28
08B4D8: 0x00000000
08B4DC: 0xFFFE31B1
08B4E0: 0x0000AC34
08B4E4: 0x00001074
08B4E8: 0x20000000
08B4EC: 0x00000C61
```

## Task 3 — handler targets extracted from table execution

Relative targets calculated from the raw table words:

- from 0x08B4CC + signed 0xFFFED029 => 0x0784F5
- from 0x08B4DC + signed 0xFFFE31B1 => 0x06E68D

Raw windows requested around those targets:

### 0x0784F5..0x078575

```asm
784F5: 50e0          str     r0, [r4, r3]
784F7: 04f8          lsls    r0, r7, #0x13
784F9: cb1b          ldm     r3, {r0, r1, r3, r4}
784FB: 4407          add     r7, r0
784FD: a9bf          add     r1, sp, #0x2fc
784FF: 01f1          lsls    r1, r6, #0x7
78501: 5903          ldr     r3, [r0, r4]
78503: 1218          asrs    r0, r3, #0x8
78505: 001f          movs    r7, r3
78507: 0423          lsls    r3, r4, #0x10
78509: 412a          asrs    r2, r5
7850B: 04f8          lsls    r0, r7, #0x13
7850D: f93b 5fd2     ldrsh   r5, [r11, #210]!
78511: 82ea          strh    r2, [r5, #0x16]
78513: 0b7c          lsrs    r4, r7, #0xd
78515: 0446          lsls    r6, r0, #0x11
78517: 4fd5          ldr     r7, [pc, #0x354]
...
```

### 0x06E68D..0x06E70D

```asm
6E68D: 01b4          lsls    r4, r6, #0x6
6E68F: 4468          add     r0, sp, r0
6E691: 8368          strh    r0, [r5, #0x1a]
6E693: 0168          lsls    r0, r5, #0x5
6E695: 0144          lsls    r4, r0, #0x5
6E697: 54eb          strb    r3, [r5, r3]
6E699: e402          b       0x6DEA1
6E69B: 4807          ldr     r0, [pc, #0x1c]
6E69D: 4bbf          ldr     r3, [pc, #0x2fc]
6E69F: 9144          str     r1, [sp, #0x110]
...
```

## Raw table-associated bytes

First record region:
```
08B4CC:
29 D0 FE FF
C4 E9 00 00
28 5F 01 20
00 00 00 00
```

Second record region:
```
08B4DC:
B1 31 FE FF
34 AC 00 00
74 10 00 00
00 00 00 20
61 0C 00 00
```

## Explicit execution note

No contiguous raw source payload for a destination covering 0x20011534..0x20011669 was identified from this table pass. The table material above is preserved verbatim for the external deep-analysis agent to interpret.

## Status

This is an execution checkpoint only. No semantic conclusion about the table format, compiler, handler type, compression, or 0x47/0x48 gate is asserted here.
