# AUTONOMOUS PASS 19 — PROVIDER VTABLE / ADDRESS-BASE CORRECTION + GET/SET CLOSURE — 2026-11-22

## Critical breakthrough

The previous PASS 18 correction contained a second address-base error.

The canonical firmware is executed/repacked at runtime base 0x08010000, while the static PROJECT notation used by the decompiler is 0x08000000 + RAW.

Therefore runtime pointers must be translated as:

RUNTIME = PROJECT + 0x10000
PROJECT = RUNTIME - 0x10000
RAW = RUNTIME - 0x08010000

This explains why runtime vtable addresses such as 0x080A31F0 appeared as erased bytes when they were incorrectly read at RAW offset 0xA31F0.

Correct location:
- provider runtime vptr: 0x080A31F0
- provider PROJECT address: 0x080931F0
- provider RAW offset: 0x931F0

At RAW 0x931F0 the canonical BIN contains:
31 db 01 08 / 79 db 01 08 / 00 00 00 00 / 00 00 00 00 / ff 17 06 08 ...

## NEW-HARD — provider slot 0 = GET

Provider vtable slot 0:
- runtime target: 0x0801DB31 (Thumb)
- PROJECT target: 0x0800DB31
- implementation begins at RAW 0xDB30.

The implementation derives a storage/address context, calls 0x08014BBA twice to obtain two 16-bit halves, combines them into one 32-bit value, stores the result through the output pointer, and returns success/failure.

The call site in FUN_0801143C is decisive: r0 = provider object [manager+0x7178], r1 = PID, r2 = output frame on stack, then provider vptr -> slot 0 -> BLX.

Therefore provider.GET(PID, output) -> status is HARD at the machine/interface level.

## NEW-HARD — provider slot 1 = SET

Provider vtable slot 1:
- runtime target: 0x0801DB79 (Thumb)
- PROJECT target: 0x0800DB79
- implementation begins at RAW 0xDB78.

The implementation dispatches on a type byte and writes/updates provider-side value through 0x08014C14.

The periodic synchronization path FUN_08011368 is decisive: provider = [this+0x7178], vptr = [provider], slot +0x04, r1 = PID, r2:r3 = current 32-bit value, then BLX. It reaches slot +4 when provider-side value differs from local value.

Therefore provider.SET(PID, value, type) -> status is HARD.

## NEW-HARD — address mapping correction

| Runtime | PROJECT | RAW |
|---|---|---|
| 0x080A31F0 | 0x080931F0 | 0x931F0 |
| 0x080A44F0 | 0x080944F0 | 0x944F0 |
| 0x080A4544 | 0x08094544 | 0x94544 |
| 0x080A4568 | 0x08094568 | 0x94568 |
| 0x0801DB31 | 0x0800DB31 | 0xDB31 |
| 0x0801DB79 | 0x0800DB79 | 0xDB79 |

## CLOSED
- concrete provider object 0x20008D64
- provider vptr runtime 0x080A31F0
- provider vtable physical contents
- provider slot 0 implementation
- provider slot 1 implementation
- provider GET contract
- provider SET contract
- static registration -> provider GET
- periodic sync -> provider GET
- periodic mismatch -> provider SET

## Still OPEN
1. Complete provider interface beyond slots 0/1.
2. Exact persistence/EEPROM/flash semantics inside provider implementation.
3. Full 260-row catalog -> provider PID mapping.
4. Full 660 runtime record population/mapping.
5. Complete local WRITE -> publication sink -> CAN 0x0584/0x42 bridge.
6. Sidecar class 1/2/3 exact semantics.

## Negative result reclassification

The earlier statement that provider vtable slot contents were unavailable because RAW 0xA31F0 was 0xFF is REJECTED.
The underlying observation was correct, but the address translation used to interpret it was wrong. The corrected RAW location is 0x931F0.

## Evidence
Canonical BIN SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Size: 0x1F0000.
No inferred provider slot target is used.