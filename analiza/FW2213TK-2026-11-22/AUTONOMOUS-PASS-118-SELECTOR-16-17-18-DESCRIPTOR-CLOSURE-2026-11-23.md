# AUTONOMOUS PASS 118 — SELECTOR 16/17/18 DESCRIPTOR POINTER CLOSURE — 2026-11-23

## Hard closure

Raw C064 decompilation gives exact descriptor records:

| selector | descriptor | word0 callback/config | word1 |
|---:|---:|---:|---:|
| 16 | RAW 0x38790 | PROJECT 0x08048493 | 0 |
| 17 | RAW 0x38790 | PROJECT 0x08048493 | 0 |
| 18 | RAW 0x387B8 | PROJECT 0x080485A1 | 0 |

Therefore selector 16 and 17 use exactly the same descriptor and callback/config function. Their hard distinction in this construction path is the state byte: selector 16 -> +0x12B = 0x11; selector 17 -> +0x12B = 0x10. Selector 18 uses a different callback/config function: 0x080485A1; case 18 itself does not write +0x12B.

All three use the same runtime-object constructor: FUN_08039494 -> FUN_080394A8 -> object+0x110, with object+0x10C pointing at +0x110.

## Descriptor semantics

Existing PASS 29/30 hard evidence establishes that word0 of these 8-byte records is an executable callback/config function pointer and that the resulting object has vtable 0x0809F848. These are not passive resource IDs.

16/17 callback: 0x08048493. 18 callback: 0x080485A1.

## Correction

More precise chain:
16/17 -> descriptor 0x38790 -> callback/config 0x08048493 -> common runtime object constructor/install.
18 -> descriptor 0x387B8 -> callback/config 0x080485A1 -> common runtime object constructor/install.

## Next

Recover/decompile bodies of 0x08048493 and 0x080485A1, trace their reads/writes and calls into presenter/PID/resource code, then assign semantic identity to selectors 16/17/18. In parallel continue S1.2 XREF for 0x08054848, 0x08056028, 0x08056040.

No dynamic Claude claim is changed.
