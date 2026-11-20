# CHECKPOINT — 47290 SOURCE CONTEXT — 2026-11-20

## New hard correction

The object previously called "record" in:
0803EE30 -> 080484B0

is not proven to be the generic 0x2C CAN parameter-engine record.

Raw BIN shows r4 is the caller's original object:
- FUN_08048624 starts with mov r4,r0 and directly calls FUN_0803EC18.
- FUN_0807EB36 starts with mov r4,r0 and directly calls FUN_0803EC18.
- inside FUN_0803EC18:
  - r4+0x0C -> slot/index minus 1
  - r4+0x07 -> variant/state byte
  - r4+0x08 -> pointer passed as stack arg 2
- 080484B0 forwards that pointer as param_7 to 08047334.
- 47334 consumes param_7[slot] as TypedText ID.

Thus the decisive unresolved field is:
OBJECT_R4 + 0x08 -> six u16 TypedText IDs.

## 0803EC18 model

Raw code resolves panel IDs:
0x4A..0x53 = decimal 74..83
through FUN_08036FF2.

First six correlate with burner/blower characteristic parameters:
74 -> 0x2252 burner burner feeder
75 -> 0x2261 blower characteristic 20%
76 -> 0x2262 blower characteristic 40%
77 -> 0x2263 blower characteristic 60%
78 -> 0x2264 blower characteristic 80%
79 -> 0x2265 blower characteristic 100%

This makes 0803EC18 a parameter/model refresh dispatcher, not an obvious dedicated language routine.

## Direct BL xrefs from raw BIN

0803EC18:
- 0804864A
- 0807EB5C

080484B0:
- 0803EE30

08047334:
- 080484D4

## DAT_0803EEC0

Raw bytes at 0x3EEC0:
34 15 01 20
50 16 01 20
94 15 01 20

=> RAM pointers:
0x20011534
0x20011650
0x20011594

Each occurs exactly once as a raw 32-bit literal in the BIN.

## Language

Still hard:
- menu selector 90 = Language
- parameter 3 = Language
- RAM 0x20021FAA
- range 0..30
- 8 TypedText language tables

But:
- selector 90 -> 47290 is OPEN
- Language parameter -> 47290 is OPEN
- 47290 = language selector is now WEAK/OPEN, leaning negative.

## Next decisive trace

08048624 / 0807EB36
-> class/vtable/factory
-> object initialization
-> writer of object+0x08
-> six u16 IDs
-> TypedText IDs
-> decode in all 8 language tables.

Do not infer the six IDs from proximity, old projects, or language-table count.