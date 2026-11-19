# BATCH — RAW CORRECTION: 0x158/0x11C + 469E8 + 47040 ARE CASCADE PATH, NOT 370A — 2026-11-19

## 1. Critical correction to the previous raw-BIN batch

The previous batch correctly recovered `FUN_08047040` as a 1..3 selector over four repeated objects, but its semantic labels were too broad.

The raw mapping table at `0x08037820` proves:

- internal index `0x158` -> external parameter ID `0x351A`
- internal index `0x11C` -> external parameter ID `0x350C`

Project registry identifies:
- `0x351A` = **Cascade slaves number**, u8, range 1..3, default 1.
- `0x350C` = **Is this device cascade master**, u8, range 0..1.

Therefore the call:

```
FUN_0803E45C
   model[0x158] = parameter 0x351A = cascade slaves number
   model[0x11C] = parameter 0x350C = cascade master flag
        ↓
FUN_08047040
        ↓
four repeated component states
```

is a **cascade UI path**, not the Boiler image selector 0x370A path.

This path must NOT be used as the bridge:
`370A -> model[0x158]`.

## 2. FUN_08047040 exact raw semantics

Raw instructions:

- enable == 0: clear +0xB05, +0xCA1, +0xE3D and then +0x969.
- enable != 0:
  - selector 1 -> +0xB05
  - selector 2 -> +0xB05 +0xCA1
  - selector 3 -> +0xB05 +0xCA1 +0xE3D
  - +0x969 receives enable.

Thus this is exactly consistent with a cascade-master flag plus number-of-slaves selector.

## 3. 469E8 bitmap child offset — raw correction

In raw `FUN_080469E8`:

```
r8 = parent + 0x13C
...
movs r0,#0x0E
strh r0,[sp]
mov r1,sp
mov r0,r8
BL FUN_080307BC
```

Therefore the hard raw fact is:

**469E8 -> Bitmap/resource child at parent +0x13C -> resource ID 14.**

The earlier `child +0x4F` classification for 469E8 is not supported by this raw constructor trace and must be withdrawn.

The constructor also has text/other children and is registered as a composite component.

## 4. DAT_08046CC0 / DAT_08046CC4 — still rejected as vtable

Raw constructor stores:
- DAT_08046CC0 = `0x0807C660`
- DAT_08046CC4 = `0x08079F00`

These resolve into UTF-16 text/resource space, including text beginning with `žeistas kambario daviklis 2`.

Therefore neither constant may be treated as the final C++ vptr without additional runtime proof.

## 5. New hard mapping: internal index -> external parameter

At `0x08037984` the raw data is:

```
0x0121 -> 0x370A
```

This is part of the larger internal-index/external-ID map beginning around `0x08037820`.

Thus the external 370A parameter has an internal model/index representation of `0x121`.

This is important, but it does NOT yet prove that any current UI function reads internal index 0x121. The mapping table is data-driven.

## 6. 370A handler field is data, not Thumb code

Raw `0x0801AB7E` is inside a dense data region. The bytes around it are table-like 16/32-bit values, not executable Thumb.

The same heterogeneity is visible in neighboring parameter fields:
- 3709 -> executable code,
- 370A -> data table,
- 370B -> data table,
- 370C -> executable code,
- 370D -> executable code.

Therefore the table field is a generic **handler/conversion/metadata boundary**, not a uniform C function pointer.

For 370A specifically, `0x0801AB7E` must currently be treated as a data-table/descriptor address.

## 7. 370A RAM address remains an external symbol fact, not yet a direct raw-code reference

Known parameter metadata:
- external ID `0x370A`
- RAM storage `0x20021FA6`
- logical range 1..3
- snapshot raw 259 -> logical 3.

A raw scan found no literal 32-bit occurrence of `0x20021FA6` and no MOVW/MOVT pair constructing that absolute address. Therefore the firmware likely reaches this storage through a generic configuration/parameter object or base+offset mechanism rather than a direct absolute reference.

This is a major narrowing of the trace.

## 8. Revised architecture

```
external parameter 0x370A
       |
       v
internal index 0x121
       |
       +-- generic parameter engine [OPEN]
       |
       +-- storage 0x20021FA6 [KNOWN]
       |
       +-- handler/data boundary 0x0801AB7E [DATA, not function]
       |
       +-- UI consumer [OPEN]
              |
              +-- variable Bitmap/resource selection [OPEN]


SEPARATE CASCADE PATH

0x351A (Cascade slaves number)
0x350C (Cascade master)
       |
       v
FUN_0803E45C
       |
       v
FUN_08047040
       |
       v
four 469E8 composite instances
       |
       +-- each contains Bitmap resource 14 at +0x13C
```

## 9. Next attack

Do NOT follow `0x158` anymore for 370A.

Next priority:

1. Recover the generic parameter engine path from **internal index 0x121**.
2. Identify the data structure that maps `0x121 -> 0x370A -> storage 0x20021FA6 -> handler 0x0801AB7E`.
3. Identify how the handler/data-table pointer is consumed.
4. Find UI code that requests internal index `0x121`, or equivalent external ID `0x370A`.
5. Independently search for the variable resource-ID writer around the actual Home boiler visual component.
6. Keep the cascade/469E8 branch separate unless a hard pointer/call/data edge reconnects it to 370A.

No 370A -> 011/012/013/014 mapping is proven.
