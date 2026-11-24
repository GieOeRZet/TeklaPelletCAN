# BATCH — MULTIPASS HOME BOTTOM CORRECTION + CONTENT HOST — 2026-11-19

## PASS 1 — hard correction

The earlier interpretation “47244 + 47290[6] = seven horizontal bottom tiles” is REJECTED.

Hard geometry from FUN_08047334:
- six repeated records are arranged vertically;
- Y values are approximately 50, 84, 118, 152, 186, 220;
- therefore FUN_08047290 is a vertical list/section, not six horizontal bottom-bar tiles.

This correction is now authoritative.

## PASS 2 — FUN_08047244

FUN_08047244:
- creates FUN_08034A90(param_1 + 0x18)
- positions the resulting component at X=50, Y=55
- child/component has its own vptr DAT_0804728C.

FUN_08034A90 is 740 bytes and does NOT contain a hard bitmap ID 11..14.
Current evidence says it builds a series of textual/control elements.

Therefore:
- it is not the boiler bitmap;
- it remains a candidate for a distinct UI/control region;
- “MENU” is not yet proven for this component.

## PASS 3 — Home root architecture

FUN_0803E5AC creates independent components:
- +0x213D -> FUN_0802E716 : dynamic content host
- +0x23DC -> FUN_08047244
- +0x24B7 -> FUN_08047290
- +0x258F -> FUN_08047604
- +0x289B -> FUN_08047E54

This is stronger than the old “bottom bar” model: these are sibling components inside the Home root.

FUN_0802E716 is 648 bytes and is instantiated at root +0x84F4.
Nearby helper block:
- FUN_08034A2C
- FUN_08034A40
- FUN_08034A54
- FUN_08034A68
- FUN_08034A7C
- FUN_08034A90 (740 B)
- FUN_08034D74 (420 B)

This host/control cluster is now the strongest next target for reconstructing the visible Home content.

## PASS 4 — 370A relation

0x370A remains independently closed as:
- Boiler image selector
- u8, range 1..3
- default 1
- RAM 0x20021FA6
- registration/callback raw 0x0801AB7E
- observed snapshot value 3

The correct architectural question is now:
370A -> callback/model update -> dynamic content host 2E716 and/or visual child,
not “370A -> bottom slot”.

## PASS 5 — CO2 remains separate

CO2 concrete chain remains:
0x08056D2C -> 0x0805D948 -> 0x080612E0.

Its internal widgets include:
- +0xA4 -> TypedText 58 “Ogrzewanie 2”
- +0x85C -> TypedText 68 “Moc 2”
- +0x8B4 -> TypedText 348 “Błąd wygaszania”
- +0x8EC -> TypedText 460 “Liczba kotłów slave”

No evidence yet connects this directly to the Home sibling 47244/47290 components.

## Next attack

1. Fully decode FUN_08034A90 child creation and all TypedText/resource IDs.
2. Fully decode FUN_0802E716 and FUN_08034D74, including child offsets and parent links.
3. Trace 0x370A callback 0x0801AB7E toward those Home components.
4. Only after that return to 47604 for bitmap/visual content.
5. Keep 47290 classified as vertical list until a separate parent/clip geometry proves otherwise.
