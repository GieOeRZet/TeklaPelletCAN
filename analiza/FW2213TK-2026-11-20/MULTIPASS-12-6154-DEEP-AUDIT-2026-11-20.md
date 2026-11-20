# MULTIPASS-12 — 6154 Level-3 Deep Audit — 2026-11-20

## Passes completed
1. Exact opcode/control-flow audit of all 17 gate offsets.
2. Function-boundary recovery for all 17 wrappers.
3. Direct-caller xref audit: each wrapper has one direct caller.
4. Parent-constructor inspection.
5. Cross-instance structural comparison.
6. Access-byte source verification: all use context+0x158.
7. Threshold verification: literal 3, branch is BLT/skip.
8. Child identity verification: +0x23C is inserted only at level >=3.
9. Add-child helper verification: all use FUN_08030380.
10. Touch/event handler audit of FUN_0802FB04.
11. Slider/value update audit: +0x60 is incremented/decremented; +0x64 is upper bound.
12. Update-path audit: FUN_08035786 is a UI/slider geometry interpolation path, not itself a CAN writer.

## Closed findings
- 17 separate wrapper functions: 4A510, 4A9EC, 4B1D4, 4C104, 4E9DC, 4F400, 4F744, 4FE9C, 5019C, 50458, 50714, 50A28, 50CE4, 50FA0, 5125C, 51518, 5FAB4.
- Direct callers: 407D0, 40DD2, 41318, 427C4, 483F0, 4B4CC, 4B67C, 4BEAA, 4C6CC, 4CA48, 4CD50, 4CFA4, 4D250, 4D5DC, 4D878, 4DB8C, 5F80A.
- All 17 perform the same semantic gate: read context+0x158; if <3 skip; otherwise add parent+0x23C.
- The same wrappers continue by adding parent+0x210.
- The common tree also includes +0x78, +0x11C, +0xD8, +0x17C, +0x1B0, +0xA4, +0x1E4.
- FUN_0802FB04 proves +0x23C = increment control and +0x284 = decrement control.
- Increment condition: +0x60 < +0x64. Decrement condition: +0x60 >= 1.
- Thus level 3 changes real widget-tree membership and real interaction, not only menu visibility.

## Additional strong clue
Several parent constructors explicitly write object/context +0x12A before invoking the wrapper:
- 405C4 = 2 -> 4A510
- 40C5A = 2 -> 4A9EC
- 411A8 = 4 -> 4B1D4
- 4B348 = 5 -> 4F400
- 4B622 = 2 -> 4F744
- 5F466 = 2 -> 5FAB4
A separate constructor at 4D634 uses a switch on +0x12B selecting values 0x29, 0x28, 0x2A..0x31. Exact human semantics remain OPEN.

## Important correction
The call from FUN_0802FB04 to FUN_08035786 does NOT by itself prove a CAN/record write. 35786 is a numeric/slider geometry interpolation helper. Do not label it a parameter write path.

The handler's separate virtual-object path through parent+0x3D8 remains the correct next target for discovering the actual model/record callback.

## Configuration strings observed in the same firmware family
Autoconfig activation; Outside temperature sensor configuration; Heating configuration; Hot water configuration; Buffer configuration; Solar configuration; Lambda module presence; Return to boiler temperature sensor; Is this device cascade master; Pressure sensor; Additional fuel storage; EGT sensor type; Energy meter type; Airflow meter; Boiler image selector; Profile number; Main module type; CH expansion module type.

These strings are not yet assigned to the 17 level-3 pages.

## Next exact targets
A) trace parent+0x3D8 callback object and its vtable +0x08/+0x0C;
B) recover initialization of +0x60/+0x64 for each parent;
C) trace parent+0x140 slider/value widget to parameter record;
D) resolve each parent title/string/resource;
E) cross-gate each page against CO/CWU/buffer/solar/lambda/cascade/additional-storage configuration;
F) synthesize access levels 0/1/2/3 and record tree deltas.

Evidence policy: [FW] direct firmware/disassembly; [STRONG] independent converging traces; [OPEN] unresolved. Current TeklaPelletCAN UI is not used as behavioral source of truth.
