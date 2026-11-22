# NewEstyma — RECORD SEMANTIC CLOSURE 04 — 2026-11-22

Direct reading of FUN_08011812 + FUN_08014734 now closes the semantic roles of the three 5-byte descriptors and all five value types.

## HARD — descriptor semantics

For R(i) = base + i*0x2C:

- +0x14 = minimum/lower-bound descriptor.
- +0x1C = maximum/upper-bound descriptor.
- +0x24 = default/reset descriptor.

Reason: with param_6 == 1, FUN_08011812 performs:
1. decode R+0x1C;
2. decode incoming value;
3. if R+0x1C < incoming -> status 6;
4. decode incoming value;
5. decode R+0x14;
6. if incoming < R+0x14 -> status 7.

Therefore +0x14 is lower bound and +0x1C is upper bound. This is direct comparison order, not a naming inference.

FUN_0801113A obtains +0x24 through FUN_0801155A and writes it back through FUN_08011812 when FUN_0801100C detects a value outside the descriptor range. Therefore +0x24 is the default/reset/repair value.

## HARD — exact value types

FUN_08014734 decodes the descriptor type byte:

| type | representation |
|---:|---|
| 1 | unsigned 8-bit |
| 2 | unsigned 16-bit |
| 3 | unsigned 32-bit |
| 4 | signed 16-bit |
| 5 | signed 32-bit |

The type-5 signedness is now closed because FUN_08014734 explicitly returns the 32-bit payload through signed int semantics.

FUN_08011812 destination writes agree:
- type 1 -> byte
- type 2 -> 16-bit
- type 3 -> 32-bit
- type 4 -> signed 16-bit
- type 5 -> 32-bit signed path

## HARD — descriptor construction arguments

FUN_0801143C maps registration arguments:

- param_5 -> +0x14 = minimum
- param_7 -> +0x1C = maximum
- param_11 -> +0x24 = default/reset
- param_4 -> +0x10 = runtime value type
- param_2 -> +0x08 = PID
- param_3 -> +0x0C = current-value storage pointer

Thus the registration primitive already contains the complete parameter definition tuple:

PID + storage + type + min + max + default.

## Parameter record canonical model

R(i):

+0x08 PID:u16
+0x0C storage:u32*
+0x10 type:u8
+0x14 min:{value:u32,type:u8}
+0x1C max:{value:u32,type:u8}
+0x24 default:{value:u32,type:u8}

Body size = 0x2C exactly, with +0x11..+0x13, +0x19..+0x1B, +0x21..+0x23, +0x29..+0x2B as remaining bytes.

The +0x2C/+0x30 adjacent-slot sidecar behavior remains separate from the canonical body.

## Remaining highest-value target

The parameter engine is no longer the blocker at the generic type/range/default level. The next macro closure should be:

1. extract registration tuples for the full 260 catalog;
2. map each PID to storage pointer, type, min, max, default;
3. map each PID to mapper position(s), CAN producer/consumer and UI resource/widget;
4. resolve the adjacent-slot sidecar +0x00..+0x07 semantics.
