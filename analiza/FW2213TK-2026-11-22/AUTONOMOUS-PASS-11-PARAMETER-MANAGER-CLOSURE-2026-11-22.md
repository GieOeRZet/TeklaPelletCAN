# AUTONOMOUS PASS 11 — PARAMETER MANAGER CALLER / REGISTRATION CLOSURE

Date: 2026-11-22

## HARD

### 1. FUN_0801143C has one direct caller in the recovered decompilation

Whole decompiled blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a was searched for FUN_0801143c(. Only one caller site is recovered: FUN_08001AE4.

FUN_08001AE4 performs exactly three visible static registrations:

- PID 0x3500 — Main module type — sidecar/class 3
- PID 0x3502 — CH expansion module type — sidecar/class 3
- PID 0x350B — Profile number — sidecar/class 3

Thus the three previously known static class-3 registrations are not three examples among many visible direct callers: they are the complete set of direct FUN_0801143C calls in this decompiled export.

### 2. Dynamic registration remains possible, but it is not represented by a direct FUN_0801143C call

The absence of additional direct callers does NOT prove that only three parameters exist. The 260-slot catalog and dynamic mapper remain independent evidence. Any additional registration must therefore reach the registration routine indirectly, through generated/decompressed/runtime data, a wrapper, or another dispatch mechanism not represented as a direct C call in the export.

### 3. Registration sidecar semantics sharpened

FUN_0801143C writes:
- R+0x2C = param_10
- R+0x30 = param_9

and only when param_10 is 2 or 3 does it call the provider at object+0x7178 during registration.

The three visible static registrations all use param_10=3. Therefore provider synchronization at registration is definitely exercised by these three static parameters.

### 4. +0x7178 is confirmed in three distinct lifecycle phases

The recovered code invokes provider GET through +0x7178 during:
1. registration in FUN_0801143C;
2. periodic synchronization in FUN_08011368;
3. subsequent SET when provider/local values differ.

This closes the lifecycle contract but not the concrete provider implementation.

## Scheduler conclusion

FUN_08010FCE still has no direct caller in the decompiled blob. Combined with the single direct registration caller result, the remaining missing edges are increasingly likely to be runtime-installed/indirect framework edges rather than ordinary C call sites.

Do not promote this likelihood to HARD without runtime/object evidence.

## Tooling

Added:
- tools/re_scan.py
- tools/test_re_scan.py
- tools/RE-SCANNER-README.md

The scanner is evidence-first and separates direct XREFs from unresolved indirect dispatch.

## OPEN

- concrete +0x7178 vtable/object
- concrete +0x7180 vtable/object
- scheduler/framework route to FUN_08010FCE
- full dynamic registration mechanism
- exact sidecar 1/2/3 semantics
- second source compared by FUN_0801100C