# AUTONOMOUS PASS 29 — RUNTIME CLASS → CALLBACK/DESCRIPTOR LAYER — 2026-11-22

## Objective

Continue from PASS 28 by closing the common UI construction boundary at PROJECT 0x08037F88 and resolving the first-level runtime-class dispatch into the callback/configuration layer.

Canonical BIN SHA-256 was revalidated before analysis:

1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Tooling

Added:

- `tools/ui_dispatch_scan.py`
- `tools/test_ui_dispatch_scan.py`

The scanner resolves the 21-byte TBB table at RAW 0x3C076, follows the firmware's small trampoline branches, and records the resolved handler. It deliberately stops at inline/special branches instead of scanning into the next TBB case.

The regression test covers all 21 class entries and the known special cases.

## HARD — exact 21-class dispatch

The runtime class byte is read at PROJECT 0x0803C06A:

- LDRB r0,[r0,r1]
- CMP r0,#0x14
- BHI -> RAW 0x3C16A
- TBB [pc,r0]

TBB table starts at RAW 0x3C076.

Exact table bytes:

0B 11 15 19 1D 24 30 36 3C 42 2A 48 5A 7A 80 63 74 6E 68 4E 54

The resolved class -> first-level handler graph is:

| class | TBB target RAW | resolved handler |
|---:|---:|---:|
| 0 | 0x3C08C | PROJECT 0x08038008 |
| 1 | 0x3C098 | PROJECT 0x08038130, r1=1 |
| 2 | 0x3C0A0 | PROJECT 0x08038130, r1=2 |
| 3 | 0x3C0A8 | PROJECT 0x08038130, r1=3 |
| 4 | 0x3C0B0 | PROJECT 0x08038130, r1=4 |
| 5 | 0x3C0BE | PROJECT 0x080381E4 |
| 6 | 0x3C0D6 | PROJECT 0x080383B0 |
| 7 | 0x3C0E2 | PROJECT 0x08038278 |
| 8 | 0x3C0EE | PROJECT 0x080382CA |
| 9 | 0x3C0FA | PROJECT 0x080382A6 |
| 10 | 0x3C0CA | PROJECT 0x0803809C |
| 11 | 0x3C106 | PROJECT 0x080384B0 |
| 12 | 0x3C12A | inline special path |
| 13 | 0x3C16A | PROJECT 0x0803850C |
| 14 | 0x3C176 | immediate return |
| 15 | 0x3C13C | PROJECT 0x08042318 |
| 16 | 0x3C15E | PROJECT 0x0803856C |
| 17 | 0x3C152 | PROJECT 0x08038568 |
| 18 | 0x3C146 | PROJECT 0x08038574 |
| 19 | 0x3C112 | PROJECT 0x08038638 |
| 20 | 0x3C11E | PROJECT 0x080382EE |

This is a HARD machine-level dispatch graph.

## HARD — common construction tail 0x08037F88

PROJECT 0x08037F88 is the shared tail used by the generic runtime-class handlers.

It receives:

- r0 = parent/current object
- r4 = parent + 0x10C
- r5 = parent + 0x110
- r1 = selected callback/config descriptor pointer
- stack space = 0x14 bytes

At 0x08037F88:

1. LDRD r2,r3,[r1]
2. MOV r1,r0
3. MOV r0,sp
4. BL PROJECT 0x08039494
5. MOV r1,r0
6. MOV r0,r5
7. BL PROJECT 0x080394A8
8. STR r5,[r4]
9. return

PROJECT 0x08039494 initializes the temporary object:

- loads vtable pointer 0x0809F848 from literal pool;
- stores it at [sp];
- stores parent/current object at [sp+4];
- stores r2/r3 at [sp+8]/[sp+0xC].

PROJECT 0x080394A8 copies:

- [temporary+4] -> [r5+4]
- [temporary+8/+C] -> [r5+8/+C]

Thus the generic class path creates/initializes the object stored at:

- parent + 0x110

and assigns it the runtime vtable:

- 0x0809F848

This is a HARD object-construction boundary.

## HARD — static callback/config descriptor pool

The selected r1 values are pointers into a static table region around RAW:

- 0x386A8 .. 0x387D8

The entries are 8-byte records:

- word 0 = callback/config function pointer
- word 1 = 0

Representative entries used by the runtime-class handlers include:

| descriptor RAW | stored word |
|---:|---:|
| 0x386D8 | 0x08048037 |
| 0x386F0 | 0x080480CB |
| 0x38708 | 0x0804817F |
| 0x38710 | 0x080481A1 |
| 0x38720 | 0x08048213 |
| 0x38738 | 0x08048357 |
| 0x38750 | 0x08048411 |
| 0x38760 | 0x0804844D |
| 0x38770 | 0x08048313 |
| 0x38778 | 0x08048335 |
| 0x38780 | 0x080483D5 |
| 0x38790 | 0x08048493 |
| 0x38798 | 0x080484D1 |
| 0x387A0 | 0x080484EF |
| 0x387A8 | 0x0804854B |
| 0x387B0 | 0x0804852D |
| 0x387B8 | 0x080485A1 |
| 0x387C0 | 0x080485C9 |
| 0x387C8 | 0x0804861B |
| 0x387D0 | 0x08048677 |
| 0x387D8 | 0x08048659 |

The values are recorded as raw firmware data. Their business meaning is not assigned.

## HARD — classes 1..4 are parameterized variants of one constructor

The TBB trampolines for classes 1..4 explicitly load:

- r1=1
- r1=2
- r1=3
- r1=4

and all converge on PROJECT 0x08038130.

PROJECT 0x08038130:

- writes r3 to parent+0x12B;
- writes r1 to parent+0x12C;
- then selects a descriptor from the static pool and enters 0x08037F88.

Therefore:

runtime class 1..4
-> shared constructor
-> selector state +0x12B/+0x12C
-> descriptor
-> object +0x110
-> vtable 0x0809F848

is HARD.

## HARD — selected descriptor examples

The generic handlers select the following descriptor records depending on their state byte:

- class 0 -> 0x386D8 -> 0x08048037
- class 1..4 -> 0x38708 or 0x38710 -> 0x0804817F / 0x080481A1
- class 5 -> 0x38720 -> 0x08048213
- class 6 -> 0x386F0 -> 0x080480CB
- class 7 -> 0x38780 -> 0x080483D5
- class 8 -> 0x38738 -> 0x08048357
- class 9 -> 0x38750 -> 0x08048411
- class 10 -> 0x38760 -> 0x0804844D
- class 11 -> 0x38798 / 0x387A0 -> 0x080484D1 / 0x080484EF
- class 13 -> 0x387A8 / 0x387B0 -> 0x0804854B / 0x0804852D
- class 16/17 -> shared PROJECT 0x08038488 path -> descriptor around 0x38790
- class 18 -> descriptor around 0x387B8
- class 19 -> 0x387D0 / 0x387D8
- class 20 -> 0x38770 / 0x38778

These are binary control/data relationships, not semantic names.

## HARD — callback 0x08048037 has direct selector-state effect

The function at PROJECT 0x08048037:

- calls the global helper;
- writes byte value 1 to object+0x12A;
- returns.

Therefore at least one callback/config function selected by the runtime-class descriptor pool directly mutates the UI object state.

This proves the descriptor pool is behaviorally active, not merely metadata.

## HARD — classes 16/17 share a separate descriptor builder

Classes 16 and 17:

- write 0x10 / 0x11 to object+0x12B;
- converge on PROJECT 0x08038488;
- that path constructs the object at object+0x110 using the same 0x08039494/0x080394A8 pair.

Thus classes 16/17 share construction machinery but differ in selector state.

## HARD — class 18 is a distinct object+0x110 builder

PROJECT 0x08038574:

- creates a temporary descriptor using a static pair around RAW 0x387B8;
- copies it into parent+0x110;
- returns.

It does not pass through the same parent+0x10C selector-byte setup as classes 1..13.

## HARD — class 14 remains a true empty branch

Class 14 target:

- RAW 0x3C176
- instruction POP {r4,pc}

No construction path follows.

## HARD — class 12 is genuinely special

Class 12 starts at RAW 0x3C12A and executes:

- load object+0x08;
- PROJECT 0x080373BA;
- increment returned value;
- PROJECT 0x080373E6;
- branch to RAW 0x3C250.

PROJECT 0x080373E6:

- computes remainder modulo 8 from its input;
- builds a parameter-manager call;
- calls PROJECT 0x08011812 with manager pointer and logical parameter key 3;
- returns the 16-bit result.

This is structurally different from the generic page/widget construction path.

The exact business meaning remains OPEN.

## HARD — class 15 is a direct object+0x0C path

Class 15:

- loads [object+0x0C];
- branches to PROJECT 0x08042318.

PROJECT 0x08042318:

- computes object+0x422C;
- constructs a second pointer from RAW/PROJECT address 0x080037B0;
- branches to PROJECT 0x0802EADE.

Therefore class 15 bypasses the generic 0x08037F88 constructor.

Its exact UI meaning remains OPEN.

## STRONG

- The runtime-class layer is a behavior/configuration selector feeding a second-level callback/object construction layer.
- The object at parent+0x110 is likely the per-screen/per-widget behavior object because it receives a vtable and callback/config pointer, but the semantic label is intentionally not promoted.
- The static function-pointer pool around RAW 0x386A8..0x387D8 is likely a dispatch/configuration registry for these UI behaviors.
- Runtime classes 1..4 appear to represent variants of the same widget/page family rather than four unrelated screens.

## OPEN

1. Identify the vtable slots of 0x0809F848 and map them to the callback object behavior.
2. Trace the selected callback functions (0x08048037, 0x080480CB, 0x0804817F, etc.) to concrete widget/resource/text/PID accesses.
3. Resolve class 12's parameter-manager operation and the role of key 3.
4. Resolve class 15's 0x42318 -> 0x2EADE object/navigation path.
5. Resolve the callback descriptor selected for each state branch and connect it to screen/widget IDs.
6. Continue screen -> widget -> text/bitmap/resource -> PID -> CAN.
7. Continue writer/alias search for 0x20005EF0 and 0x20005F08.
8. Continue provider slots/persistence and 260-row matrix in parallel.

## REJECTED / CORRECTED

- Runtime class == direct screen ID: rejected.
- Generic class 12/15 paths being equivalent to the 0x08037F88 constructor: rejected.
- Treating the descriptor pool as plain data without execution relevance: rejected; at least 0x08048037 is directly executed through the constructed object path.
