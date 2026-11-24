# AUTONOMOUS PASS 120 — CALLBACK CFG EVIDENCE BOUNDARY + S1.2 AUDIT — 2026-11-23

## Objective
Continue S1.3 from PASS 119 without inheriting semantics from containing functions, and audit available repository evidence for the parallel S1.2 targets.

## 1. Callback entry 0x08048493

Hard facts:
- Descriptor 0x38790 contains Thumb entry pointer 0x08048493.
- Ghidra function table identifies containing function FUN_08048468, start 0x08048468, size 0x48 bytes.
- Therefore the entry is exactly +0x2B from the containing function start.
- Existing decompilation of FUN_08048468 is available, but it is a whole-function decompilation and does not expose a CFG/basic-block split at +0x2B.
- The whole-function body contains the write at param+0x8F95 and calls FUN_0802E652, FUN_08034D74, FUN_0802EADE and FUN_08032316.
- This is NOT sufficient evidence that entry 0x08048493 executes all of those operations.

Existing repository evidence shows FUN_0803EC18 recognizes type 0 -> FUN_08048468, type 3 -> FUN_080484B0, type 4 -> FUN_080484F0, type 5 -> FUN_08048520. Existing analysis identifies these as host/content switching operations.

Status: OPEN at instruction/CFG level.

## 2. Callback entry 0x080485A1

Hard facts:
- Descriptor 0x387B8 contains Thumb entry pointer 0x080485A1.
- Ghidra function table identifies containing function FUN_0804858A, start 0x0804858A, size 154 bytes (0x9A).
- Therefore the entry is exactly +0x17.
- Repository currently contains the function boundary but no decompiled body/raw instruction listing for FUN_0804858A.

Status: OPEN at instruction/CFG level.

## 3. Consequence for selector 16/17/18

From PASS 118/119:
- selector 16 -> descriptor 0x38790 -> entry 0x08048493, plus context +0x12B=0x11
- selector 17 -> same descriptor/entry 0x08048493, plus +0x12B=0x10
- selector 18 -> descriptor 0x387B8 -> entry 0x080485A1; case 18 itself does not write +0x12B
- all three use the common object construction/install path.

Therefore selector distinction cannot currently be reduced to three independent callback functions. For 16/17 the same entry point is reused and the hard discriminator is the surrounding context state.

## 4. S1.2 repository audit

Available committed evidence confirms:
- helper 0x08054848 exists in function coverage and is already hard-associated with UI keys 0xB0 / 0xCD in prior passes.
- setter candidates 0x08056028 and 0x08056040 exist in function coverage.
- existing negative audit establishes 0xF4 -> PID 0x2115 via setter 0x08056040; 0xF5 -> PID 0x2280 via setter 0x08056028; 0xF3 -> PID 0x2114 is absent as an exact presenter pair.
- No new repository text artifact found in this pass exposes the missing caller/basic-block relationship for 0x08054848, 0x08056028, or 0x08056040.

This is a negative result, not evidence that the setters are unused.

## 5. Evidence boundary / next executable target

The remaining blocker for exact callback semantics is the raw instruction/CFG artifact covering:
- 0x08048493 through the end of FUN_08048468
- 0x080485A1 through the end of FUN_0804858A

The current repository does not expose those instruction bodies. Do not manufacture a semantic mapping from function-start decompilation.

For S1.2, next useful artifact is an XREF/callsite listing or raw decompilation around 0x08054848, 0x08056028 and 0x08056040.

## Verdict

No semantic overclaim made. PASS 120 narrows the exact evidence boundary and preserves the 1:1 rule: entry-point semantics require entry-point CFG evidence.