# TeklaPelletCAN — MAIN MENU / ACCESS SECOND-PASS — 21-RECORD CORRECTION MULTIPASS
Date: 2026-11-20
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## EXECUTIVE RESULT

This pass found a critical control-flow error in the previous handoff.

The earlier claim that constructor FUN_08042160 consumes only the first 15 records and leaves the final six OPEN is **withdrawn**.

The raw code proves a two-stage construction:

1. first loop consumes records 0..14;
2. if access-level byte is nonzero, a second loop consumes records 15..20;
3. after both stages, a separate 21-iteration pass processes the 21 constructed row slots against a runtime 21-byte state array.

Therefore the 21-record table at 0x42348 is not merely a 15-record menu table with unrelated trailing data. The trailing six are part of the same constructor's second-stage row population, but they are **access-level conditional**.

This also explains why their bitmap family differs radically from the first 15: they belong to a second-stage/access-dependent visual set.

The exact semantic meaning of every trailing selector remains OPEN until the row state, touch/navigation, and surrounding screen context are traced.

---

# PASS 01 — RAW RECORD LAYOUT

Raw table starts at file offset 0x42348.

Each record is 6 bytes:

- +0x00 = selector/state byte/word
- +0x02 = bitmap_A
- +0x04 = bitmap_B

Verified records:

| idx | selector | bitmap_A | bitmap_B |
|---:|---:|---:|---:|
| 0 | 0 | 60 | 83 |
| 1 | 10 | 61 | 85 |
| 2 | 1 | 62 | 86 |
| 3 | 2 | 63 | 86 |
| 4 | 3 | 64 | 86 |
| 5 | 4 | 65 | 86 |
| 6 | 5 | 66 | 88 |
| 7 | 6 | 71 | 87 |
| 8 | 7 | 67 | 84 |
| 9 | 8 | 70 | 82 |
| 10 | 9 | 69 | 99 |
| 11 | 11 | 72 | 78 |
| 12 | 13 | 74 | 89 |
| 13 | 17 | 77 | 159 |
| 14 | 15 | 76 | 96 |
| 15 | 0 | 12 | 73 |
| 16 | 90 | 14 | 75 |
| 17 | 97 | 18 | 78 |
| 18 | 100 | 16 | 79 |
| 19 | 98 | 19 | 80 |
| 20 | 95 | 20 | 81 |

[DATA][CLOSED]

---

# PASS 02 — FIRST LOOP: EXACTLY 15 RECORDS

At FUN_08042160:

0x421DA:
- r5 = 0x0F

0x421E8:
- cmp r4,#0x0F

0x421EC:
- reads record fields from r9:
  - +2 -> bitmap_A
  - +4 -> bitmap_B
- calls FUN_0804BC6C(row, bitmap_A, bitmap_B)

0x421FA:
- reads selector at [r9+0]
- compares selector to 0x0F

0x42248:
- increments r4
- advances r9 by 6
- advances r10 by 6
- loops while r4 < 0x0F

Therefore first loop consumes records 0..14.

[FW][CLOSED]

---

# PASS 03 — CRITICAL SECOND-LOOP CONTROL FLOW

The previous analysis stopped at the first loop and missed the fact that r4 is NOT reset.

At 0x42204:
- access-level byte is read from object storage;
- if zero, execution jumps directly to 0x42248;
- if nonzero, execution enters 0x42208.

At 0x42208:
- r2 = [r10+4]
- r1 = [r10+2]
- row builder FUN_0804BC6C is called.

Then:

0x42216:
- r0 = [r10]

0x4221A:
- r5 = 0x15

0x4221C:
- compare r0 with 0x0C

0x42228:
- compare r0 with 0x0E

0x42248:
- r4++
- r10 += 6
- r9 += 6
- 0x4224E compares r4 against 0x15

Crucial fact:

After first loop, r4 == 0x0F.

The second loop therefore runs for:
0x0F, 0x10, 0x11, 0x12, 0x13, 0x14

= six iterations.

The six iterations consume table records 15..20.

[FW][CLOSED]

---

# PASS 04 — POINTER ALIGNMENT PROOF FOR RECORDS 15..20

Initial r10 is established at:

r10 = table_start - 2

During the first 15 iterations r10 advances 15*6 = 90 bytes.

Thus:

r10_after_first = table_start - 2 + 90
                 = table_start + 88

Record 14 begins at table_start + 84 and occupies +84..+89.

Therefore r10_after_first = record14 + 4.

This is deliberate.

For the second stage:

- [r10+2] = record15 selector
- [r10+4] = record15 bitmap_A? No: because the record layout is [selector, A, B], [r10+2] is bitmap_A and [r10+4] is bitmap_B.
- [r10] = record14 bitmap_B

The row builder therefore receives the second-stage record's A/B pair exactly as intended.

The first byte at r10 is a one-field look-behind marker from the previous record's B field.

[FW][CLOSED]

---

# PASS 05 — EXACT SECOND-STAGE RECORDS

The six second-stage iterations map as follows:

| iteration | r10 source | selector | A | B | look-behind [r10] |
|---:|---|---:|---:|---:|---:|
| 1 | record15 +4 | 0 | 12 | 73 | 96 |
| 2 | record16 +4 | 90 | 14 | 75 | 73 |
| 3 | record17 +4 | 97 | 18 | 78 | 75 |
| 4 | record18 +4 | 100 | 16 | 79 | 78 |
| 5 | record19 +4 | 98 | 19 | 80 | 79 |
| 6 | record20 +4 | 95 | 20 | 81 | 80 |

The exact selector values are therefore genuinely part of the same constructor's second-stage data.

[FW][CLOSED]

---

# PASS 06 — ACCESS-LEVEL CONDITION IS HARD PROOF

The branch at 0x42204:

- loads the object's access-level byte;
- cbz -> skips the second-stage construction when zero.

Thus:

access level == 0:
  records 0..14 are populated by this constructor;
  records 15..20 are not populated in this stage.

access level != 0:
  records 0..14 are populated;
  records 15..20 are additionally populated.

This is stronger than the earlier generic observation that access level "changes row state".

It proves that access level changes the **number/content of row objects constructed**.

[FW][CLOSED]

---

# PASS 07 — SECOND-STAGE VISUAL FAMILY IS NOT AN UNRELATED FLASH TAIL

The six A/B pairs are:

- 12 + 73
- 14 + 75
- 18 + 78
- 16 + 79
- 19 + 80
- 20 + 81

These were previously classified as qualitatively different from the first menu icons.

That visual observation remains valid, but the interpretation changes:

They are not proven unrelated data.

They are now proven to be second-stage resources consumed by the same constructor, conditional on access level.

Therefore their different dimensions are evidence for a different **access-level/secondary visual mode**, not evidence that they are outside this screen class.

[FW][DATA][STRONG]

---

# PASS 08 — SECOND-STAGE SPECIAL MARKER IS A LOOK-BEHIND FIELD

The second-stage code tests:

[r10] == 0x0C
or
[r10] == 0x0E

Because r10 is record14+4 for the first second-stage iteration and then advances by 6, [r10] is the previous record's bitmap_B byte.

For the actual six iterations, the observed values are:

0x60, 0x49, 0x4B, 0x4E, 0x4F, 0x50

which do not equal 0x0C or 0x0E.

Therefore the 0x0C/0x0E branches are not triggered by the six observed iterations in the current table snapshot.

This is important: do not reinterpret 0x0C/0x0E as selectors 12/14. They are tested against the one-byte look-behind field.

[FW][CLOSED]

---

# PASS 09 — SELECTOR 0 DUPLICATE IS NOW BETTER CONSTRAINED

There are two selector=0 records:

record 0:
0 -> A60/B83

record 15:
0 -> A12/B73

They are not duplicates in the same construction phase.

- record 0 belongs to the always-built first stage;
- record 15 belongs to the access-level conditional second stage.

Thus selector 0 is context-sensitive in this constructor.

The second occurrence must not be collapsed into the first merely because the selector value matches.

[FW][STRONG]

---

# PASS 10 — 21-ROW POST-PROCESSING LOOP

After the two construction stages, the code enters a separate loop.

At 0x4226A:
- r7 = 0

At 0x4226E:
- row pointer starts at object +0x380

At 0x42278:
- calls FUN_0803C178(model, r7)

At 0x4227E:
- if resolver returns false, row is not passed to the next routine.

At 0x42288:
- r7++
- row pointer += 0x274

At 0x42290:
- loop continues while r7 < r5

At this point r5 = 0x15.

Therefore the constructor has a separate 21-slot capability pass over row objects spaced by 0x274.

This is a major architectural clue:

The table contains 21 logical row slots, and the configuration resolver is applied to all 21 slots after construction.

[FW][CLOSED]

---

# PASS 11 — ROW OBJECT STRIDE

The 21 post-processing row objects are spaced:

0x274 bytes

The row base begins at:

object + 0x380

and each iteration adds 0x274.

This means the menu/secondary-row object storage is a fixed-size array of 21 row objects.

The 15+6 split is therefore a construction policy, not a different object array.

[FW][CLOSED]

---

# PASS 12 — SEPARATE 21-ITERATION ACCESS UPDATE PATH

A second function starts at 0x422C8.

It:

- sets r8 = object +0x524
- sets r7 = 0x15
- loads a global pointer from literal @0x42314
- loops exactly 21 times
- advances r8 by 0x274 each iteration
- advances the external pointer by one byte
- if object access-state byte is nonzero and the external byte equals 0x0E, it calls:
  FUN_08032F08(row)
  then FUN_0803C270(model,...)

This is independent evidence that the firmware treats the menu/row family as a 21-slot structure.

The external pointer resolves to RAM address:

0x20005F08

The firmware binary itself does not contain the runtime contents of that RAM table.

[FW][STRONG]

---

# PASS 13 — WHAT THE 21-SLOT ARCHITECTURE MEANS

The combined structure is now:

raw table 0x42348
    |
    +-- records 0..14 -> always constructed
    |
    +-- records 15..20 -> constructed only when access != 0
    |
    v
21 row objects, stride 0x274
    |
    +-- capability resolver applied to row slots 0..20
    |
    +-- separate access/update pass can touch all 21
    |
    v
screen/container tree

This is much stronger than a simple static "menu list".

[STRONG]

---

# PASS 14 — CONTRADICTION / STALE-HYPOTHESIS CHECK

Withdraw from previous batch/master:

- "constructor processes only first 15 records"
- "trailing six records are not consumed by this constructor"
- "trailing six are unresolved secondary context because no consumer references table tail"

Replace with:

- constructor first stage consumes 15 records;
- access-dependent second stage consumes six more;
- all 21 row slots participate in later capability/access processing;
- the exact semantic screen role of the second-stage six remains OPEN.

The earlier evidence that the six assets differ visually was correct, but the causal interpretation was wrong.

This correction is directly derived from raw control flow and pointer arithmetic.

[FW][CLOSED CORRECTION]

---

# PASS 15 — IMPLEMENTATION CONSEQUENCE

The final ESP implementation must model this constructor as:

MenuRow[21]

with at least:

row[0..14]:
  base construction

row[15..20]:
  access_level != 0 ? construct : leave absent/unconstructed

then:

for i in 0..20:
  capability_visible = FUN_0803C178(model,i)

and a separate access/update stage.

Do NOT implement:

"15 fixed menu items + six unrelated resources"

Do NOT implement:

"21 always-visible menu items"

The correct current model is:

**21-slot row family with conditional second-stage construction and later capability/access processing.**

---

# OPEN ITEMS AFTER THIS CORRECTION

1. What are the exact widget classes/vtables of the 21 row objects?
2. Why are records 15..20 constructed only for access != 0?
3. What are selectors 0/90/97/100/98/95 in that second-stage context?
4. What is the semantic role of bitmap pairs 12/73, 14/75, 18/78, 16/79, 19/80, 20/81?
5. What is the exact meaning of the 0x0C/0x0E look-behind test?
6. What is the runtime contents/producer of RAM array 0x20005F08?
7. What does FUN_08032F08 do to the selected row?
8. What does FUN_0803C270 do after the access marker is found?
9. What are the exact geometry values for row objects and children +0x60/+0x8C/+0xF8?
10. What touch/callback path does each row use?

---

# NEXT ATTACK

Priority A:
Trace FUN_08032F08 and FUN_0803C270.

Priority B:
Trace all constructors/methods for the row object at object+0x380+n*0x274.

Priority C:
Recover the concrete vtable/class family of the row objects.

Priority D:
Trace all writes/reads of RAM 0x20005F08.

Priority E:
Trace selector-dependent navigation from row objects.

Priority F:
Only after A-E, assign semantic labels to the six access-dependent records.

