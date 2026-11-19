# BATCH — RAW BIN RECOVERY / 469E8 + 47040 + 370A CORRECTION — 2026-11-19

## 1. Raw firmware is now available

File:
- `FW2213TK_kopia.bin`
- size: `2,031,616` bytes = `0x1F0000`
- SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

Vector table confirms the expected STM32/Thumb mapping:
- initial SP = `0x20013F28`
- reset vector = `0x080A3209`
- raw address mapping is consistent with flat image base `0x08000000`.

Therefore raw machine code can now be checked directly instead of inferred from decompiled.c.

## 2. 0x0801AB7E is NOT executable code in this raw BIN

Raw offset:
`0x0801AB7E - 0x08000000 = 0x1AB7E`.

Bytes at that location begin:
`ff 0f 00 00 00 00 00 00 f8 ff ...`

Disassembly as Thumb produces only nonsensical data-like instructions and long repeated patterns. The region is clearly a data/resource block, not a normal ARM/Thumb function body.

This is a major correction to the previous interpretation.

The current parameter-table field saying:
`370A -> 0x0801AB7E`
must NOT be interpreted as a normal executable callback address.

The earlier conclusion that callback fields may point into larger code blocks remains valid for 3709/370C/370D, but **370A specifically points into a raw data/resource region in this firmware image**.

This makes the 370A field more likely to be a data pointer, resource/table boundary, encoded handler descriptor, or a value consumed by a higher-level dispatcher rather than a direct BL/BLX target.

## 3. Neighboring callback addresses — raw verification

### 3709 -> 0x0801425C
Raw code is executable Thumb and is inside a larger code block. Around the address:
- `0x08014250`: BL to `0x08014534`
- `0x0801425C`: `adds r2,r4,r0`
- the block continues as normal code.

### 370B -> 0x08015CCC
Raw bytes are data, not a normal code entry. The surrounding region contains monotonic table-like values.

### 370C -> 0x0801659E
Executable Thumb. It is inside a larger state/logic routine. At the exact address:
`cmp r1,r3` / branch follows.

### 370D -> 0x08016614
Executable Thumb and inside the same routine as 370C. At the exact address:
`cmp r2,r0` followed by conditional branch.

So the neighboring fields are heterogeneous:
`code / data / code / code`.

This strongly suggests the table field is not uniformly a simple C function pointer type.

## 4. 317AE raw machine code — +0x50 is real

Raw disassembly of `FUN_080317AE` proves:

```
child = registry[index]
if active:
    vptr = *(uint32_t*)child
    method = *(uint32_t*)(vptr + 0x50)
    BLX method(child)
```

The relevant raw sequence is:

`317f8..3180a`:
- read active byte,
- obtain registered object pointer,
- load first word of object,
- load word at `+0x50`,
- `BLX`.

Thus `+0x50` is not a documentation artifact. It is a real runtime indirect-call boundary.

## 5. Critical correction: DAT_08046CC4 is NOT proven to be a vtable

This is the most important raw-BIN correction.

In `FUN_080469E8`:

- `0x080469F4` loads literal at `0x08046CC0` and stores it at object +0.
- `0x08046A04` loads literal at `0x08046CC4` and stores it at object +0.

Raw contents:

`DAT_08046CC0 = 0x0807C660`
`DAT_08046CC4 = 0x08079F00`

But `0x08079F00` is visibly UTF-16 text data, beginning with:

`"žeistas kambario daviklis 2"`

Likewise `0x0807C660` points into UTF-16 text.

Therefore `DAT_08046CC4` cannot be accepted as a C++ vtable pointer.

The previous project statement:
`finalny vptr komponentu 469E8 = DAT_08046CC4`
is **invalidated by raw evidence**.

The function `FUN_080469E8` is still real and still constructs the same visual composite, but its first word is demonstrably a text/resource pointer at the end of the constructor.

## 6. 469E8 still has the hard Bitmap ID=14 fact

Raw code confirms:

`0x080469E8` calls `FUN_080307BC` with a child around `+0x4F` and value `0x0E`.

The writer itself is independently confirmed at `0x080307BC`:
- reads the supplied 16-bit value,
- writes it to child +0x26,
- invokes child vtable +0x38/+0x3C for dependent geometry/state.

So:
- 469E8 -> Bitmap child +0x4F = retained fact.
- initial resource ID 14 = retained fact.
- `DAT_08046CC4) as vptr = rejected.

## 7. Four 469E8 instances are real

`FUN_0803E34C` calls `FUN_080469E8` at:
- parent + `0x944`
- parent + `0xAE0`
- parent + `0xC7C`
- parent + `0xE18`

The corresponding constructor object stride is `0x19C` in the earlier parent layout.

The four instances are therefore confirmed as a repeated visual/data component. Their semantic identity (boiler images vs another icon/room-sensor component) remains OPEN.

## 8. NEW: FUN_08047040 is a direct 1..3 selector over the four 469E8 instances

This is the first raw-BIN path found that directly manipulates the four instance-local state bytes.

`FUN_08047040(parent, selector, enable)` performs:

- if enable == 0:
  - child2 + `0x25` = 0
  - child3 + `0x25` = 0
  - child4 + `0x25` = 0
  - child1 + `0x25` = 0

- if enable != 0 and selector == 1:
  - child2 + `0x25` = 1

- if selector == 2:
  - child2 + `0x25` = 1
  - child3 + `0x25` = 1

- if selector == 3:
  - child2 + `0x25` = 1
  - child3 + `0x25` = 1
  - child4 + `0x25` = 1

- finally:
  - child1 + `0x25` = enable

The offsets match exactly:

```
parent + 0x944 + 0x25 = parent + 0x969
parent + 0xAE0  + 0x25 = parent + 0xB05
parent + 0xC7C  + 0x25 = parent + 0xCA1
parent + 0xE18  + 0x25 = parent + 0xE3D
```

This is hard raw evidence of a 1..3 selector controlling state of four repeated 469E8 instances.

## 9. FUN_08047040 caller is FUN_0803E45C

There is exactly one direct BL to `FUN_08047040` in the raw image:

`FUN_0803E45C + 0x7E` approximately, at `0x0803E4DA`.

The caller loads:
- model index `0x11C` -> converted to u8 -> passed as enable,
- model index `0x158` -> converted to u8 -> passed as selector.

Call:

`FUN_08047040(parent+0xC, value(0x158), value(0x11C))`

Therefore the actual chain currently proven is:

```
model index 0x158
       +
model index 0x11C
       ↓
FUN_08047040
       ↓
four 469E8-instance state bytes
```

This is much stronger than the previous generic "vtable +0x50 -> unknown update" hypothesis.

## 10. Important semantic warning

Do NOT yet rename model index `0x158` to "370A".

We have two separate facts:

A:
`370A -> RAM 0x20021FA6 -> table field 0x0801AB7E`

B:
`model[0x158] + model[0x11C] -> FUN_08047040 -> four 469E8 instances`

The bridge A -> B is still missing.

However, B is now a concrete visual-state control path and is an extremely strong candidate for the branch that ultimately determines which of the repeated components are active.

## 11. New interpretation of 469E8

Because the constructor stores localized UTF-16 strings at object +0, and creates a Bitmap 14 plus several TypedText children, 469E8 should no longer be treated as "confirmed boiler-image class".

The hard classification is now:

**469E8 = repeated composite visual widget containing Bitmap resource 14 + multiple text children + runtime registration.**

Its semantic identity is OPEN.

This is safer and matches raw evidence.

## 12. New main architecture

```
370A
  |
  +-- RAM 0x20021FA6
  |
  +-- table field 0x0801AB7E
          |
          +-- NOT direct Thumb code in raw BIN
          +-- UNKNOWN descriptor/resource/dispatcher edge


MODEL / HOME UPDATE
  |
  +-- FUN_0803E45C
        |
        +-- model[0x158]
        +-- model[0x11C]
        |
        +-- FUN_08047040
              |
              +-- parent+0x969
              +-- parent+0xB05
              +-- parent+0xCA1
              +-- parent+0xE3D
                    |
                    +-- four 469E8 repeated instances


469E8 constructor
  |
  +-- child +0x4F
  +-- FUN_080307BC(..., 14)
  +-- Bitmap ID 14
  +-- text children
  +-- registration via FUN_080318B4
```

## 13. Next attack

The next raw-BIN pass must NOT start by guessing a vtable at DAT_08046CC4.

Priority order:

1. Identify the actual runtime dispatch structure used by the object registered from 469E8.
2. Trace how the 469E8 object +0 first word can coexist with `317AE -> child[0] -> +0x50`.
3. Resolve the exact semantic meaning of model indices `0x158` and `0x11C`.
4. Search for where `0x20021FA6` is copied/transformed into model index `0x158), or where both originate from the same parameter.
5. Compare the four 469E8 instance state bytes with their child visibility/update methods.
6. Only then reconnect 370A to the 1..3 selector and resource/Bitmap path.
7. Keep `011/012/013/014` mapping explicitly OPEN until a direct resource-ID write or selection table is recovered.

## 14. Bottom line

The raw BIN changed the investigation substantially:

- `0x0801AB7E` is data, not normal code.
- `DAT_08046CC4` points to UTF-16 text, not a vtable.
- `FUN_080317AE +0x50` is a real indirect runtime dispatch boundary.
- `FUN_080469E8` really creates a Bitmap-14 composite.
- Four 469E8 instances are real.
- `FUN_08047040` is a newly recovered hard selector path for values 1..3 controlling those four instances.
- `FUN_0803E45C` supplies that selector from model index `0x158` and enable from `0x11C`.
- The missing bridge is now much narrower: **370A/RAM 0x20021FA6 -> model 0x158 (or another common state) -> FUN_08047040**.

No mapping 370A=1/2/3 -> Bitmap 11/12/13/14 is accepted yet.
