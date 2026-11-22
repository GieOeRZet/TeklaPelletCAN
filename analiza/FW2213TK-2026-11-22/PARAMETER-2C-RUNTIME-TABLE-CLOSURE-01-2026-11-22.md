# NewEstyma — Runtime Parameter Table / 0x2C Record Closure 01 — 2026-11-22

Firmware: `FW2213TK_kopia.bin`
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
Branch: `ccr-be8a1bcb-5t76j0`

## Status

[NEW-HARD] The parameter engine does not operate only on the previously catalogued 260-slot table.

A direct Thumb disassembly of `FUN_080115F6` proves a runtime table rooted at `0x20008D84` with a fixed record stride of `0x2C`, scanned for up to `0x294 = 660` records.

## Direct proof — FUN_080115F6

Relevant instructions from RAW evidence:

```
0x0801161E: r0 = 0
0x08011620: r1 = r5 + 0x08
0x08011624: ldrh r2, [r1]
0x08011628: cmp r2, r3
...
0x0801162E: ldrh r2, [r1, #0x2C]
...
0x08011634: r2 = r1 + 0x58
0x0801163A: r0 += 1
0x0801163C: ldrh r3, [r2]
...
0x08011644: ldrh r2, [r2, #0x2C]
...
0x0801164E: r1 += 0xB0
0x08011650: cmp r0, #0x294
0x08011654: blt 0x08011624
...
0x0801165C: r1 = #0x2C
0x0801165E: r0 *= r1
0x08011660: r0 += r5
0x08011662: ldr r1, [r0, #0x0C]
0x08011664: ldr r1, [r1]
0x08011666: str r1, [sp]
0x08011668: ldrb r0, [r0, #0x10]
```

The same function is entered with `r5` as the parameter-record base in the resolver/parameter paths; the project documentation independently identifies that base as `0x20008D84`.

## Proven record fields

For a record at:

`record = 0x20008D84 + index * 0x2C`

the following fields are directly established:

| Offset | Evidence | Proven role |
|---:|---|---|
| +0x08 | `LDRH` used in PID comparison | 16-bit parameter ID |
| +0x0C | `LDR r1,[record+0x0C]` then `LDR r1,[r1]` | pointer to current-value storage; second load obtains current value |
| +0x10 | `LDRB` | parameter type tag |
| +0x2C | next record | fixed record stride |
| +0x58 | record + 2×0x2C | confirms repeated record geometry |
| +0xB0 | record + 4×0x2C | confirms four-record block geometry |

The function compares successive IDs at +0x08, stepping by 0x2C, and can examine indices 0..659.

## Important consequence

The previously established:

- 260 unique parameter slots,
- 260 unique catalog IDs,

must NOT be treated as the complete runtime parameter-record table.

The new evidence proves a larger runtime structure capable of containing **660 records**.

Therefore:

```
260-slot catalog
        !=
complete 0x20008D84 runtime record table
```

The 260-slot table is still valid as its own catalog/index layer. The runtime record table is a separate, larger structure.

## Resolver relationship

The established resolver:

`0x08010FC2`

is called throughout the firmware and participates in the parameter engine. The direct `FUN_080115F6` evidence shows that parameter lookup operates on the 0x2C runtime records and uses the record's +0x08 PID and +0x10 type.

The exact complete semantic layout of every remaining field is still OPEN.

## What is now closed

[NEW-HARD]

1. Runtime parameter records have fixed size `0x2C = 44 B`.
2. Runtime table base is `0x20008D84` in the established parameter-engine path.
3. The table is scanned with a hard upper bound of `0x294 = 660` records.
4. PID is at record +0x08 and is compared as u16.
5. Current-value storage pointer is at record +0x0C; dereferencing it once yields the current value.
6. Type tag is at record +0x10 and is read as u8.
7. Record-to-record stride is independently demonstrated at +0x2C, +0x58 and +0xB0.

## Still OPEN

- Complete field map for offsets 0x00..0x2B.
- Meaning of record +0x2C status/commit field as used by `0x08011368`.
- Exact relationship between the 660 runtime records and the 260 catalog slots.
- Whether all 660 entries are populated/valid at runtime or whether some are reserved/empty.
- Exact descriptor ownership and instance mapping.
- Complete CAN-ID mapping across the 660-record universe.

## Evidence source

Primary byte-level evidence: `RAW_PACKET21_OPEN3_P3.txt`, generated from the canonical firmware BIN. The decisive disassembly is the body of `FUN_080115F6` around RAW `0x0115F6`.

No semantic mapping beyond the directly observed fields is asserted.
