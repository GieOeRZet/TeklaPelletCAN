# BATCH — MULTI-PASS VERTICAL TRACE / 370A + MODEL + 469E8 — 2026-11-19

## Cel
Wykonano wielopoziomowy trace zamiast pojedynczego punktu: parameter table -> callback boundary -> model layer -> active module -> binding function -> Home widget -> Bitmap writer -> asset.

## Pass 1 — parameter neighborhood
[FW/DATA]
0x370A is a real parameter:
- name: Boiler image selector
- u8
- range 1..3
- default 1
- RAM 0x20021FA6
- registration/callback field 0x0801AB7E
- snapshot encoded raw 259 => logical value 3.

Neighboring parameters 0x3709, 0x370B, 0x370C, 0x370D have callback fields 0x0801425C, 0x08015CCC, 0x0801659E, 0x08016614.

## Pass 2 — callback boundary
[FW]
0x0801AB7E is not a normal Ghidra function entry in functions.txt. The recognized function map has entries through ~0x08019462 and then a gap before later code. Therefore the table field must be treated as a callback/handler boundary, not a named C function.

Important implication: searching only function names cannot close 370A.

## Pass 3 — model database
[FW]
FUN_0801417C builds a boiler model/data table containing explicit model names such as Bio Compact 10/18 kW, Draco Bio Compact FBII, Draco Bio, Tytan Bio.

[STRONG]
There is a distinct model-identification/data layer.

[NONE FOUND]
No exported direct path 370A <- model database.

## Pass 4 — active module
[FW]
FUN_080314BA() returns the singleton active module/controller via DAT_08031A8C.

This same accessor is used by:
- Heating instance/class logic,
- UI builders,
- 469E8,
- 47290,
- other screen components.

Therefore the UI binding architecture is centralized around the active module object.

## Pass 5 — binding function
[FW]
FUN_080469E8 ends:
FUN_080318B4(FUN_080314BA(), param_1)

The exact implementation of FUN_080318B4 is not present in searchable decompiled.c text, although functions.txt confirms it is a real 134-byte function at 0x080318B4.

[STRONG]
The component is explicitly registered/bound against the active module/controller.

## Pass 6 — 469E8 widget
[FW]
FUN_080469E8 creates:
- parent W=70, H=150,
- Bitmap child at +0x4F,
- Bitmap resource ID 14,
- Y=20,
- X centered from resource width,
- four TypedText/style children.

Bitmap ID is not selected from 370A in the constructor.

## Pass 7 — writer closure
[FW]
FUN_080307BC writes resource ID directly to child+0x26 and invokes resource dimension methods.

No direct exported callsite was found that later invokes FUN_080307BC on the four 469E8 children with IDs 11/12/13.

Therefore the unresolved update path is indirect:
- vtable,
- parent traversal,
- callback/binding,
- or data-driven component update.

## Pass 8 — four-slot parent
[FW]
FUN_0803E34C creates four identical 469E8 instances:
+0x251, +0x2B8, +0x31F, +0x386
with byte stride 0x19C.

It also creates helper +0x213 via FUN_080469D4:
- vptr DAT_080469E4
- parent
- callback/object pointer
- callback/object metadata.

This helper is a strong binding boundary but not yet proven to select the bitmap.

## Pass 9 — Home root
[FW]
FUN_0803E5AC is a strong Home/Main root candidate and creates multiple independent components, including:
- +0x84F4 -> FUN_0802E716 (host/container)
- +0x92DC -> FUN_08047290 (six-slot component)
- +0x963C -> FUN_08047604
- +0xA26C -> FUN_08047E54
- +0xA5FC/+0xA628 -> FUN_08038ED0.

However, no direct proof yet connects FUN_0803E34C to this Home root.

## Pass 10 — 370A -> asset
[NEGATIVE]
No direct exported chain:
370A -> read -> switch/table -> 11/12/13/14
was recovered.

Therefore the architecture cannot yet be honestly closed at the resource-selection edge.

## New architectural model

The evidence now supports this stronger layered architecture:

MODEL/DATA
  -> parameter database (370A)
  -> model identity table (1417C)
  -> active module singleton (314BA / DAT_08031A8C)
  -> component binding (318B4)
  -> composite widget (469E8)
  -> Bitmap child (+0x4F)
  -> resource writer (307BC)
  -> Bitmap resource 14 at construction

Parallel:
Home root (3E5AC)
  -> screen components
  -> dynamic host(s)
  -> binding against same active module

The missing edge is specifically:
active module / parameter state
  -> 469E8 update method or alternate widget selection
  -> variable Bitmap resource ID.

## High-value conclusion

The correct next attack is NOT another broad search for bitmap IDs. The search space has narrowed to:
1. recover the machine-code body of 080318B4 and surrounding 08031500..31980,
2. recover vtable/data behind DAT_08046CC4 and DAT_080469E4,
3. recover raw bytes around 0801AB7E,
4. trace 370A's handler semantics,
5. connect the resulting state update to child +0x4F.

If raw firmware is available, these four targets should be disassembled together because they form one likely boundary.

## Explicit non-claims
- 370A=1/2/3 -> bitmap 11/12/13 is NOT proven.
- 370A=3 -> bitmap 14 is NOT proven.
- 3E34C is NOT yet proven to be the Home root's direct child.
- 469D4 helper is NOT yet proven to be the bitmap selector.
