# AUTONOMOUS PASS 24 — THUMB-2 BOUNDARY / POINTER-FLOW CORRECTION — 2026-11-22

## Objective

Re-run the PASS 23 attack with a Thumb-2-safe decoder, because the previous pointer-flow scanner decoded every 16-bit halfword independently. That can create false memory operations when the second halfword belongs to a 32-bit Thumb-2 instruction.

Targets:

- SRAM 0x20005EF0 — runtime class table
- SRAM 0x20005F08 — access/update table

Canonical BIN:

- size 0x1F0000 = 2,031,616 bytes
- SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Tool correction

Updated:

- tools/pointer_flow_scan.py
- tools/test_pointer_flow_scan.py

The scanner now:

1. recognizes Thumb-2 32-bit instruction prefixes;
2. advances by 4 bytes for Thumb-2 instructions, so the second halfword is never decoded as a separate Thumb-1 instruction;
3. recognizes common Thumb-2 STR/LDR immediate forms;
4. recognizes MOVW/MOVT candidates;
5. recognizes Thumb-2 PUSH.W when searching for the enclosing function start;
6. keeps SRAM targets in SRAM address space instead of incorrectly applying the firmware PROJECT/RUNTIME translation to them;
7. remains candidate/static and does not assign business semantics.

Regression test passed against the canonical BIN.

## CRITICAL CORRECTION OF PASS 23

PASS 23 reported:

- RAW 0x3C1FE
- STRB using r2
- target 0x20005EF0 + 6

This is **REJECTED**.

The real instruction stream is:

- RAW 0x3C1FC: MOV.W r1, #0x122
- RAW 0x3C1FE: second halfword of that same 32-bit instruction

Therefore RAW 0x3C1FE is not a STRB and there is no direct static proof of a write to 0x20005EF0+6 at that location.

The previous PASS 23 business-semantic OPEN derived from that alleged store is therefore removed.

## 0x20005EF0 — corrected direct pointer flow

Literal pool:

- RAW 0x3C218 = 0x20005EF0

Two literal materializations remain HARD:

| LDR RAW | PROJECT | register |
|---:|---:|---|
| 0x3C068 | 0x0803C068 | r0 |
| 0x3C17A | 0x0803C17A | r2 |

Consumers:

### PROJECT 0x0803C064

At RAW 0x3C06A:

- LDRB r0, [r0, r1]

This is a genuine indexed byte read from:

- 0x20005EF0[r1]

The load overwrites r0, so subsequent r0-relative operations are not attributed to the table.

No write to 0x20005EF0 was recovered from this pointer provenance.

### PROJECT 0x0803C178

At RAW 0x3C17C:

- LDRB r1, [r2, r1]

This is a genuine indexed byte read from:

- 0x20005EF0[r1]

The pointer in r2 is not overwritten by this operation.

No write through r2 was recovered after applying correct Thumb-2 instruction boundaries.

The apparent write at RAW 0x3C1FE is specifically rejected as the second halfword of MOV.W.

## Additional closure: runtime-class dispatch

The function around PROJECT 0x0803C064 is not merely a byte lookup.

The sequence is:

1. read runtime class byte from 0x20005EF0 using an input index;
2. compare against 0..0x14;
3. TBB dispatch through the table beginning at RAW 0x3C076;
4. dispatch to class-specific handler blocks.

The 21 TBB entries correspond to runtime class values 0..20.

The dispatch table bytes at RAW 0x3C076 are:

00 0B 11 15 19 1D 24 30 36 3C 42 2A 48 5A 7A 80 63 74 6E 68 4E 54

This is direct evidence that the runtime class table participates in a 21-class dispatch mechanism.

Important examples from the dispatch:

- class 1 -> sets r1=1, then tail-calls the common path;
- class 2 -> sets r1=2;
- class 3 -> sets r1=3;
- class 4 -> sets r1=4;
- class 5 -> common path;
- class 6 -> common path;
- class 7 -> common path;
- class 8 -> common path;
- class 9 -> common path;
- class 10..13 -> dedicated common-path tails;
- class 14 -> returns directly;
- class 15..20 -> additional dedicated paths.

The common helper at PROJECT 0x080314BA is a global-object getter:

- loads [0x08031A8C]
- returns that pointer.

Therefore the runtime-class dispatch is an object/handler selector layer, not itself a direct screen-number table.

## 0x20005F08 — corrected direct pointer flow

Literal pool:

- RAW 0x42314 = 0x20005F08

Materialization:

- RAW 0x422CE -> r5

The enclosing function begins at:

- RAW 0x422C8
- PROJECT 0x080422C8

This correction supersedes the earlier report's PROJECT 0x080522C8 label; that label came from applying the RUNTIME address base to a static PROJECT value.

At RAW 0x422DE:

- LDRB r0, [r5]

Then:

- r5 += 1
- loop count starts at 0x15
- loop terminates after 21 iterations

Therefore this function reads:

- 0x20005F08[0]
- ...
- 0x20005F08[20]

This is now a HARD 21-entry sequential read of the complete access/update table.

No write to 0x20005F08 was recovered from this pointer provenance.

## NEW cross-layer closure from the access table

The 0x20005F08 consumer provides a stronger UI-side clue.

At PROJECT 0x080422C8:

- r8 is initialized to r4 + 0x524;
- r5 points to 0x20005F08;
- r7 = 0x15;
- each iteration reads one access-table byte;
- r5 increments by 1;
- r8 advances by 0x274.

If the current access-table byte equals 0x0E:

1. r0 = r8
2. BL PROJECT 0x08032F08
3. r0 returned by 0x08032F08 is copied to r1
4. r0 = [r4 + 0x3C]
5. BL PROJECT 0x0803C270

PROJECT 0x08032F08 is closed directly:

- LDRB.W r0, [r0, #0x2C]
- return

Therefore the 0x0E path reads:

- [r8 + 0x2C]

PROJECT 0x0803C270 is also directly closed:

- reads [r0 + 0x10];
- only continues when that byte equals 1;
- then r2 = incoming r1;
- r0 = [r0 + 8];
- r1 = 0x117;
- branches to PROJECT 0x08037212.

This establishes the following machine-level chain:

0x20005F08[i] == 0x0E
-> row/object base r8
-> read [r8+0x2C]
-> PROJECT 0x0803C270
-> state gate [object+0x10] == 1
-> parameter ID 0x0117
-> PROJECT 0x08037212

This is a new HARD cross-layer boundary.

The exact business meaning of 0x0E, r8+0x2C and parameter 0x0117 is not promoted beyond the machine-level facts.

## MOVW/MOVT attack

Whole-BIN search was also performed for direct absolute materialization components:

- MOVW #0x5EF0: no hit
- MOVW #0x5F08: no hit
- MOVT #0x2000: no hit

Therefore no direct absolute MOVW/MOVT construction of either 21-byte table was found.

This does not exclude:

- base-pointer + arithmetic construction;
- pointer copies through other objects;
- indirect writes through calls;
- runtime-generated aliases.

Those remain OPEN.

## HARD

- 0x20005EF0 has exactly two recovered direct literal materializations.
- 0x20005EF0 is read byte-wise by indexed access in both consumers.
- 0x20005F08 has one recovered direct literal materialization.
- 0x20005F08 is read sequentially across all 21 entries.
- PASS 23 alleged write at 0x20005EF0+6 is REJECTED.
- RAW 0x3C1FC is MOV.W r1,#0x122; RAW 0x3C1FE is its second halfword.
- Runtime class values 0..20 feed a TBB dispatch mechanism.
- 0x20005F08 value 0x0E gates a path that reads row/object +0x2C.
- 0x08032F08 is a direct byte getter for object +0x2C.
- 0x0803C270 gates on object +0x10 == 1 and forwards value to parameter 0x0117 through 0x08037212.
- 0x080422C8 scans exactly 21 access-table bytes.

## STRONG

- The 21 runtime-class values are likely a normalized dispatch layer feeding page/widget families, because the dispatch is separate from the root selector table and ultimately reaches object methods/helpers.
- The 0x0E access-table value appears to represent a special update/activation condition, because it gates a parameter-0x0117 update path. Exact business semantics remain unproven.

## OPEN

1. Find producers/writers of 0x20005EF0 using:
   - pointer arithmetic;
   - pointer copies;
   - object fields;
   - indirect calls.
2. Find producers/writers of 0x20005F08 using the same methods.
3. Resolve the object represented by r4 in PROJECT 0x080422C8.
4. Map r8 = r4+0x524 to the 21 MenuTree rows.
5. Resolve parameter 0x0117 semantically and connect it to catalog/CAN/UI.
6. Trace each runtime class 0..20 forward from the TBB handlers into page/widget constructors.
7. Continue screen -> widget -> resource/text/bitmap -> PID -> CAN.
8. Continue the 260-row parameter matrix and provider/persistence boundary in parallel.

## REJECTED

- PASS 23 claim: STRB at RAW 0x3C1FE writes 0x20005EF0+6.
- PASS 23 semantic OPEN derived specifically from that alleged write.
- PROJECT address 0x080522C8 for the 0x20005F08 consumer.
- Treating every 16-bit halfword inside a Thumb-2 instruction as an independent instruction.

## Next highest-value attack

The next pass should not repeat the now-closed literal-pointer scan.

Priority:

1. resolve r4/r8 in 0x080422C8 and map the 0x274 stride to the 21 MenuTree rows;
2. trace 0x08037212 with PID 0x0117 backward/forward;
3. resolve all TBB class-handler tails from 0x0803C064;
4. only then attack remaining arithmetic/alias writers of the two SRAM tables.
