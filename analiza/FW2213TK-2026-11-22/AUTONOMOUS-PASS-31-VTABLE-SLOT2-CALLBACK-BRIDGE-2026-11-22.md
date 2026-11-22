# AUTONOMOUS PASS 31 — VTABLE SLOT 2 → STATIC CALLBACK DIRECT INVOCATION — 2026-11-22

## Objective

Close the remaining gap between the static callback pointer selected by the runtime-class handlers and the executable behavior of the object at parent+0x110.

## HARD — generic constructor creates a directly callable callback object

PROJECT 0x08039494 initializes:

- object+0x00 = vtable 0x0809F848
- object+0x04 = incoming parent/current UI object
- object+0x08 = incoming r2
- object+0x0C = incoming r3

The generic 0x08037F88 tail obtains r2/r3 from the selected static descriptor record.

All descriptor records used by this generic path are two-word records whose second word is zero.

Therefore the common generic path constructs:

- +0x04 = parent object
- +0x08 = selected static callback pointer
- +0x0C = 0

## HARD — vtable slot 2 reduces to direct callback invocation for generic objects

Vtable slot 2 implementation at PROJECT 0x08090398:

1. r2 = [object+0x0C]
2. r1 = [object+0x04]
3. r1 += r2 >> 1
4. when r2 >= 0:
   - r3 = [object+0x08]
5. r0 = r1
6. BX r3

For the generic object, +0x0C == 0.

Therefore the slot-2 call simplifies exactly to:

callback = [object+0x08]
argument0 = [object+0x04]
BX callback

This is a HARD executable bridge:

runtime class
-> selected descriptor
-> callback pointer at object+0x110+8
-> vtable slot 2
-> callback(parent object)

## HARD — class 0 callback example

Class 0 selects descriptor RAW 0x386D8:

- stored word = 0x08048037

PROJECT 0x08048037:

- calls the global helper;
- writes byte 1 to object+0x12A;
- returns.

Therefore the generic runtime-class construction layer can be reduced to:

class 0
-> callback 0x08048037
-> object+0x12A = 1

No semantic name is assigned to +0x12A.

## HARD — class 1..4 callback variants

Classes 1..4 share PROJECT 0x08038130 and select one of two descriptor records depending on the state byte:

- RAW 0x38708 -> 0x0804817F
- RAW 0x38710 -> 0x080481A1

Both are installed as the +0x08 callback pointer of the same vtable-backed object.

Thus classes 1..4 share one object interface while changing the callback implementation.

## HARD — vtable contains three repeated method pairs

The vtable at RAW 0x8F848 has non-zero method pairs:

- slots 2/3
- slots 8/9
- slots 14/15

Each pair has the same structural relationship:

- first method = indirect dispatch/call through +0x04/+0x08/+0x0C;
- second method = boolean/state check over the same fields.

This is direct binary evidence.

## STRONG

The object at parent+0x110 behaves like a callback/delegate object with multiple interface/base-class method pairs.

The three method pairs may represent repeated inherited interfaces or multiple ABI-visible views of the same delegate object, but this is not promoted to HARD.

## OPEN

1. Identify call sites invoking vtable slot 2 on parent+0x110.
2. Map all callback pointers to their actual state/resource/PID effects.
3. Trace callback 0x08048037 and sibling callbacks into the UI object fields.
4. Resolve vtable slot-pair semantics across the three method pairs.
5. Continue class 12/15 special paths and runtime-table mutations.
6. Continue complete screen/widget/resource/PID/CAN matrix.

## REJECTED

- Static descriptor pointer is passive metadata.
- +0x08 is merely a stored configuration pointer for the generic path.
- Runtime class directly names a screen.
