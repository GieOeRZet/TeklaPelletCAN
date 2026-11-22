# AUTONOMOUS PASS 18 — provider vtable / GET interface closure — 2026-11-22

## NEW-HARD — provider constructor
RAW 0x0800DB08:
- r0 = this
- stores vptr 0x080A31F0
- therefore 0x20008D64 -> vtable 0x080A31F0 is independently confirmed.

## NEW-HARD — vtable slot 0 = provider GET
RAW vtable:
- 0x080A31F0 + 0x00 -> 0x0801DB31

FUN_0801143C loads [manager+0x7178], loads provider vptr and calls slot 0 with (provider, PID, &value_descriptor).

FUN_0801DB31 receives this and PID, resolves the parameter entry and returns the provider value/status. This closes:
manager+0x7178 -> 0x20008D64 -> vtable 0x080A31F0 -> slot0 0x0801DB31.

## STRONG — provider slot 1
Vtable:
- 0x080A31F0 + 0x04 -> 0x0801DB79

FUN_0801DB79 is a type-dispatching value update/packing routine for types 1..5, consistent with provider SET. Exact independent caller/runtime binding remains OPEN.

## Important correction
0x080A31F0 is not a long uniformly populated table. RAW inspection shows a mixed interface/data region. Only entries backed by code-pointer plus constructor/call evidence should be promoted.

## Net result
Concrete provider object and GET endpoint are HARD.
Provider SET implementation is STRONG.
Next: independent SET binding, provider fan-out, then automatic PID cross-layer matrix.

Canonical BIN SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
