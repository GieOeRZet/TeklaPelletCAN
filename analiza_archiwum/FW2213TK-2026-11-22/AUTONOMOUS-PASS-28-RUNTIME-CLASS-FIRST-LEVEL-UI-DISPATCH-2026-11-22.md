# AUTONOMOUS PASS 28 — RUNTIME CLASS 0..20 → FIRST-LEVEL UI HANDLERS — 2026-11-22

## Objective

Close the first-level runtime-class dispatch graph from 0x20005EF0 without assigning business names prematurely.

## HARD — 21-class TBB dispatch

PROJECT 0x0803C064:

- reads class = 0x20005EF0[index];
- rejects values > 0x14;
- executes TBB using table bytes at RAW 0x3C076.

The 21 class values 0..20 dispatch as follows:

| Class | TBB target RAW | First-level handler |
|---:|---:|---:|
| 0 | 0x3C08C | 0x08038008 |
| 1 | 0x3C098 | common 0x08038130, r1=1 |
| 2 | 0x3C0A0 | common 0x08038130, r1=2 |
| 3 | 0x3C0A8 | common 0x08038130, r1=3 |
| 4 | 0x3C0B0 | common 0x08038130, r1=4 |
| 5 | 0x3C0BE | 0x080381E4 |
| 6 | 0x3C0D6 | 0x0803809C |
| 7 | 0x3C0E2 | 0x080383B0 |
| 8 | 0x3C0EE | 0x08038278 |
| 9 | 0x3C0FA | 0x080382CA |
| 10 | 0x3C0CA | 0x080382A6 |
| 11 | 0x3C106 | 0x080384B0 |
| 12 | 0x3C12A | special 0x080373BA / 0x080373E6 path |
| 13 | 0x3C16A | 0x0803850C |
| 14 | 0x3C176 | immediate return |
| 15 | 0x3C13C | object+0x0C -> 0x08042318 path |
| 16 | 0x3C15E | 0x0803856C |
| 17 | 0x3C152 | 0x08038568 |
| 18 | 0x3C146 | 0x08038574 |
| 19 | 0x3C112 | 0x08038638 |
| 20 | 0x3C11E | 0x080382EE |

This is a complete first-level static dispatch table for all 21 runtime classes.

## HARD — classes 1..4 share one constructor/update path

Class 1..4 enter PROJECT 0x08038130 with r1 equal to the class value.

0x08038130:

- computes r4 = object + 0x10C;
- writes r3 into [r4+0x1F] = object+0x12B;
- writes r1 into object+0x12C;
- derives r3 from the class:
  - class 1 -> r3=1
  - class 2 -> r3=2
  - class 3 -> r3=3
  - class 4 -> r3=4
- if class >=5, r1 would be clamped to 4, although this shared path is only entered from classes 1..4 in the recovered TBB.

It then selects a child/configuration descriptor through the object +0x110 region and branches to common UI construction at PROJECT 0x08037F88.

Therefore runtime classes 1..4 are not merely labels; they directly control fields at:

- object+0x12B
- object+0x12C

and feed the shared UI construction path.

## HARD — classes 5..10 set distinct selector bytes

The first-level handlers write:

- class 5 -> object+0x10C+0x1F = 5
- class 6 -> object+0x10C+0x1F = 6
- class 7 -> object+0x10C+0x1F = 7
- class 8 -> object+0x10C+0x1F = 7
- class 9 -> object+0x10C+0x1F = 8
- class 10 -> object+0x10C+0x1F = 9

The handlers also use object+0x110 and branch to the common UI construction path.

This proves that runtime class and internal UI selector are separate layers.

## HARD — classes 13,16,17 have explicit numeric state writes

- class 13 handler writes 0x13 to object+0x10C+0x1F.
- class 16 writes 0x10 to object+0x12B.
- class 17 writes 0x11 to object+0x12B.

These are direct binary facts.

## HARD — class 14 is a no-op return

Class 14 dispatch target is RAW 0x3C176:

- POP {r4,pc}

No further handler is executed.

This is a concrete empty branch in the 21-class runtime layer.

## HARD — special classes 12,15,19,20 are structurally different

- class 12 does not enter the common selector-byte handlers; it uses 0x080373BA/0x080373E6 and then a separate tail.
- class 15 loads object+0x0C before tailing into PROJECT 0x08042318.
- class 19 enters 0x08038638.
- class 20 enters 0x080382EE.

Therefore rows/classes 12,15,19,20 must not be forced into the generic 1..13 selector model.

## STRONG

- The runtime class byte is a UI behavior selector, not a screen ID by itself.
- object+0x10C/0x12B/0x12C are part of the runtime UI construction state.
- The shared tail at 0x08037F88 is likely a common widget/page construction engine.

## OPEN

1. Resolve PROJECT 0x08037F88 and its child descriptor source.
2. Resolve classes 0,5..13 through their common tail into concrete page/widget constructors.
3. Resolve special classes 12,15,19,20.
4. Connect object+0x10C/0x12B/0x12C to row selectors and widget resources.
5. Continue screen -> widget -> text/bitmap -> PID/CAN.
6. Continue SRAM table writer/alias search.

## REJECTED

- runtime class == direct screen/page ID;
- treating all 21 classes as one uniform handler family;
- collapsing the runtime-class table and root selector table into one layer.
