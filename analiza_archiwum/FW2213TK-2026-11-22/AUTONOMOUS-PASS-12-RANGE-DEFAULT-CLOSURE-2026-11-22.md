# AUTONOMOUS PASS 12 — RANGE ENGINE / DEFAULT REPAIR CLOSURE

Date: 2026-11-22

## HARD finding 1 — FUN_0801100C is not a second provider source

Re-reading the complete decompilation shows the compared values are entirely local parameter-record data:

- record sidecar is read from R+0x2C;
- current value/type is obtained through FUN_080115F6 and encoded by FUN_08014728;
- upper-bound descriptor is R+0x1C, with its type byte at R+0x20;
- lower-bound descriptor is R+0x14, with its type byte at R+0x18;
- the routine performs type-aware signed/unsigned comparisons;
- when current > upper bound OR current < lower bound it returns the offending PID;
- after scanning all 660 possible record slots it returns 0xFFFFFFFF when no violation is found.

Therefore the previously OPEN 'second cached/provider-related source' in FUN_0801100C is CLOSED: the second/third values are the parameter record's MAX and MIN descriptors, not a hidden provider cache.

## HARD finding 2 — FUN_0801113A is the default-repair loop

FUN_0801113A repeatedly calls FUN_0801100C. For every returned PID > 1 it:

1. obtains the record default/reset descriptor through FUN_0801155A (record +0x24);
2. commits it through FUN_08011812(..., param_5=0, param_6=1);
3. continues until FUN_0801100C returns 0xFFFFFFFF.

Thus the functional chain is:

local value -> MIN/MAX validation -> offending PID -> DEFAULT (+0x24) -> parameter commit.

## HARD finding 3 — no direct caller of FUN_0801113A in the recovered C export

Whole-blob search finds only the function definition itself. There is no direct C call to FUN_0801113A.

Likewise FUN_0801100C is only referenced by FUN_0801113A and its own definition context.

This strongly constrains the range-repair trigger to an indirect/runtime route, but that last statement remains INFERENCE until runtime evidence identifies the callback.

## Sidecar refinement

Hard facts now:
- sidecar 2/3 participate in provider GET/SET synchronization;
- sidecar 2/3 participate in range checking;
- sidecar 1 does not enter these provider/range loops;
- all three visible static registrations use sidecar 3.

Exact semantic distinction between 1 vs 2 vs 3 remains OPEN.

## New search targets

- indirect reference/registration of FUN_0801113A;
- indirect reference/registration of FUN_08010FCE;
- object containing +0x7178/+0x7180;
- runtime callback table containing either function;
- whether both callbacks belong to the same parameter-manager object.