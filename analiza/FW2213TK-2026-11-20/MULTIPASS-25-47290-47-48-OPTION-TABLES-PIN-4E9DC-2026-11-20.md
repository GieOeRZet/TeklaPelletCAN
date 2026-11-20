# MULTIPASS-25 — 47290 / 0x47 / 0x48 option tables + PIN wrapper 0x4E9DC — 2026-11-20

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Requested closures

### HARD — FUN_080480C0 presenter list filtering

Per the current deep-analysis result, FUN_080480C0 does not filter an individual key from the presenter list at presenter + 0x20.

Therefore the previously closed branch remains:
- 0x48 belongs to FUN_0803E714 case 0 (Kocioł);
- its access/list gate is context + 0x158 != 0;
- no additional 0x48-specific filter is attributed to FUN_080480C0.

### HARD — access-level separator containers

FUN_080480C0 creates two 480x50 containers:
- view + 0xA5FC
- view + 0xA628

They use bitmap resources:
- bitmap 91 = 0x5B, key 1
- bitmap 92 = 0x5C, key 2

These are the level-1 / level-2 separator elements in the ListLayout at view + 0x380.

### CORRECTION — TypedText option-table address mapping

The previous raw request at 0x7F58C..0x7F5EC used the wrong flat base interpretation and landed in a vtable/data region.

With the correct resource/runtime base 0x08010000:
- runtime 0x0807F58C -> file offset 0x6F58C
- runtime 0x0807F5EC -> file offset 0x6F5EC

The new extraction below is therefore the authoritative raw option-table span for this branch.

## Raw #1 — file offset 0x6F58C..0x6F5FF, 116 bytes

0x06F58C:
85 00 87 00 7A 00 80 00 78 00 00 00 AC 00 AD 00
AF 00 B0 00 B1 00 B3 00 B4 00 B5 00 82 00 7E 00
84 00 7C 00 82 00 7E 00 84 00 7C 00 3C 00 43 00
DE 01 E0 01 E0 01 DF 01 6C 01 6D 01 6E 01 00 00
6F 01 70 01 B6 00 B7 00 AF 00 B8 00 B9 00 00 00
AF 00 B2 00 B5 00 00 00 AF 00 A7 01 A8 01 00 00
37 00 70 47 85 00 87 00 7A 00 80 00 78 00 00 00
AC 00 AD 00

Exact:
- start 0x6F58C
- length 0x74 = 116
- end-exclusive 0x6F600
- last byte 0x6F5FF

## Raw #2 — Thumb disassembly 0x4E9DC..0x4EA50

4e9dc: b510          push    {r4, lr}
4e9de: 4604          mov     r4, r0
4e9e0: f104 0178     add.w   r1, r4, #0x78
4e9e4: 1d20          adds    r0, r4, #0x4
4e9e6: f7e1 fccb     bl      0x30380
4e9ea: f44f 708e     mov.w   r0, #0x11c
4e9ee: 1821          adds    r1, r4, r0
4e9f0: 1d20          adds    r0, r4, #0x4
4e9f2: f7e1 fcc5     bl      0x30380
4e9f6: f104 01d8     add.w   r1, r4, #0xd8
4e9fa: 1d20          adds    r0, r4, #0x4
4e9fc: f7e1 fcc0     bl      0x30380
4ea00: f44f 70be     mov.w   r0, #0x17c
4ea04: 1821          adds    r1, r4, r0
4ea06: 1d20          adds    r0, r4, #0x4
4ea08: f7e1 fcba     bl      0x30380
4ea0c: f44f 70d8     mov.w   r0, #0x1b0
4ea10: 1821          adds    r1, r4, r0
4ea12: 1d20          adds    r0, r4, #0x4
4ea14: f7e1 fcb4     bl      0x30380
4ea18: f104 01a4     add.w   r1, r4, #0xa4
4ea1c: 1d20          adds    r0, r4, #0x4
4ea1e: f7e1 fcaf     bl      0x30380
4ea22: f44f 70f2     mov.w   r0, #0x1e4
4ea26: 1821          adds    r1, r4, r0
4ea28: 1d20          adds    r0, r4, #0x4
4ea2a: f7e1 fca9     bl      0x30380
4ea2e: f7e2 fd44     bl      0x314ba
4ea32: f890 0158     ldrb.w   r0, [r0, #0x158]
4ea36: 2803          cmp     r0, #0x3
4ea38: db05          blt     0x4ea46
4ea3a: f44f 700f     mov.w   r0, #0x23c
4ea3e: 1821          adds    r1, r4, r0
4ea40: 1d20          adds    r0, r4, #0x4
4ea42: f7e1 fc9d     bl      0x30380
4ea46: f44f 7004     mov.w   r0, #0x210
4ea4a: 1821          adds    r1, r4, r0
4ea4c: 1d20          adds    r0, r4, #0x4
4ea4e: f7e1 fc97     bl      0x30380

End of requested window: 0x4EA50.

## Execution note

The 0x6F58C extraction was performed directly from FW2213TK_kopia.bin.
The 0x4E9DC disassembly was performed from the ELF wrapper generated from the same firmware binary.

This pass corrects the earlier 0x7F58C address-base mistake and supplies the requested real option-table bytes.
