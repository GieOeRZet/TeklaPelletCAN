# CHECKPOINT — 47290 / LANGUAGE / UPDATE / HOME — 2026-11-20

## Source
FW2213TK_kopia.bin
SHA256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
size 0x1F0000
runtime base 0x08010000

## Closed evidence

### 47290
- 0803E5AC + 0x92DC -> 08047290
- 6 records
- first +0xA8
- stride 0x40
- FUN_08047334:
  slot X=100
  slot Y=50+34*slot
- resources 151/152
- labels from param_7[slot]
- 484B0 forwards caller record+0x08 as param_7
- therefore record+0x08 is pointer to six u16 TypedText IDs

### Language
- TypedText tables: 8
- languages: ES, EST, EN, LT, PL, RO, SK, CZ
- 495 entries/table
- starts: 59E90, 5A64C, 5AE08, 5B5C4, 5BD80, 5C53C, 5CCF8, 5D4B4
- menu selector 90 = Language
- parameter ID 3 = Language
- type u8, range 0..30, default 0
- RAM 0x20021FAA
- associated code 0x08011D6C

### Home visual anchors
- 115 = lower-right settings/menu/power tile
- 144 = CO1 tile icon
- 174 = CWU tile icon
These are user visual correlations, not substitutes for firmware data-flow proof.

## Contradictions / stale hypotheses
- 47290 is NOT Home vertical menu.
- 47290 is NOT bottom bar.
- 47290 is NOT graph 056/057.
- 47290 is NOT proven language selector.
- 47290 is NOT proven updater screen.
- 0803E5AC is not proven to be only a static Home renderer.

## Highest-priority unresolved chain

A:
0803EC18 -> 0803EE30 -> record -> record+0x08 -> param_7 -> 6 TypedText IDs.

B:
TypedText IDs -> each of 8 language tables -> actual six strings.

C:
selector 90 -> row/callback/touch/navigation -> concrete screen factory.

D:
115/144/174 -> indirect resource table/registry -> constructor -> parent -> X/Y/W/H.

E:
Find updater boot/update factory separately. Search for SD/update/boot/version/LED paths; do not assume 47290.

## Evidence policy
No semantic claim from resource proximity alone.
No use of old HA/card geometry as firmware proof.
No "absence" claim from missing immediate resource literal when table-driven indirection is possible.
OPEN stays OPEN until constructor/data-flow/callback evidence closes it.
