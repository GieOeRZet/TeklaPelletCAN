# AUTONOMOUS PASS 131 — PROVIDER SLOT 4 FUNCTION-START CORRECTION — 2026-11-23

## Objective
Verify provider vtable slot +0x10 directly against the uploaded canonical BIN, rather than relying on the earlier function-list interpretation.

## HARD raw result
Provider vtable at RAW 0x931F0 contains slot +0x10: word 0x080617FF. Thumb-normalized code address = 0x080617FE.
Direct raw inspection of the canonical uploaded BIN at RAW 0x517FE shows 0x080617FE begins with halfword 0xB510 (push {r4,lr}), a valid Thumb function prologue; the next bytes form a complete 38-byte function body; function coverage records 0x080617FE,38,1,1,0; the following function begins at 0x08061824.

Therefore slot +0x10 is NOT an interior entry of FUN_080617DC.

It is the exact start of a separate 38-byte executable function at runtime 0x080617FE / Thumb pointer 0x080617FF / raw 0x517FE.

## Supersession
PASS 126 incorrectly classified 0x080617FF as an interior +0x23 entry of FUN_080617DC because the surrounding bytes were not checked against the actual function boundary. PASS 131 supersedes that part of PASS 126.

The correct hard statement is: provider vtable slot +0x10 -> Thumb pointer 0x080617FF -> normalized entry 0x080617FE -> distinct 38-byte executable function.

The earlier semantic label state/init is still NOT proven.

## Additional raw context
At 0x080617DC a different short routine ends immediately before 0x080617FE. The new function starts exactly at 0x080617FE, so there is no CFG ambiguity at the slot-4 entry boundary.

## Remaining OPEN
The exact semantic contract of this slot-4 function remains open until its 38-byte body is decoded/cross-referenced: inputs/arguments, return value, callers beyond the vtable dispatch, relationship to provider state/persistence.

This is now a much narrower target and can be attacked directly from raw bytes/XREFs.