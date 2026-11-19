# BATCH: C064 direct class+instance materialization and dispatch boundary — 2026-11-19

## New hard result

Re-read the complete decompiled.c around FUN_0803C064 and the surrounding object/parameter-engine code.

### 1. C064 is the strongest currently known runtime class+instance dispatcher

FUN_0803C064(param_1,param_2) executes:

    class = DAT_0803C218[param_2]

For table values 1..4 it then does, in the same function:
- class 1 -> module+0x12B = 1, module+0x12C = 1
- class 2 -> module+0x12B = 2, module+0x12C = 2
- class 3 -> module+0x12B = 3, module+0x12C = 3
- class 4 -> module+0x12B = 4, module+0x12C = 4

The byte from DAT_0803C218[param_2] is converted to bVar4, normalized to uVar6, written to +299, and the clamped instance is written to +300. Descriptor selection follows via DAT_08038708 / 0x8038710 / 0x8038718 depending on +0x12A, then FUN_08039494 and installation at +0x10C/+0x110.

### 2. C064 is a multi-class dispatcher, not a CO-only routine

DAT_0803C218[param_2] can select 0, 1..4, 5..10, 0x0B, 0x0C, 0x0E, 0x0F, 0x10/0x11, 0x12, 0x13/0x14 and default descriptor paths. Therefore the table is a general object-classification table. The 1..4 entries are the exact path that can represent CO instances, but assigning specific param_2 indexes to CO1..CO4 still requires recovering the table contents.

### 3. Class/instance is created atomically

param_2 -> DAT_0803C218[param_2] -> class/instance value b -> +0x12B=b -> +0x12C=min(b,4) -> descriptor selection.

For values 1..4, class and instance are deliberately equal. This is stronger than merely observing FUN_08037D00 later normalizes +0x12C.

### 4. Parameter engine confirms +0x12C is operational

FUN_08036FF2, FUN_080370C0 and FUN_08037212 read the module +0x12C and use it as an instance offset for the first parameter table. Therefore the direct runtime chain is:

C064 class/instance -> module +0x12B/+0x12C -> generic parameter lookup base + instance - 1 -> parameter record -> UI/CAN consumers.

### 5. No direct C call-site is emitted

A complete literal search of the decompiled blob still finds only the definition of FUN_0803C064; there is no emitted direct call. The missing boundary is therefore:

unknown caller / callback / vtable / startup table -> FUN_0803C064(param_1,param_2) -> DAT_0803C218[param_2]

The firmware contains extensive indirect dispatch/vtable calls and Ghidra did not emit all data tables.

### 6. Immediate next targets

1. Recover DAT_0803C218 (108-byte classification table) from Ghidra memory/data export or raw BIN.
2. Find the indirect entry into FUN_0803C064 by tracing object/vtable tables around the C064 class and nearby constructors.
3. Recover the source of param_2.
4. Map table positions whose values are 1,2,3,4 to static CO1..CO4 parameter families: 0x2032..0x2035, 0x2048..0x204B, 0x2064..0x2067.
5. Only after this connect the result to configuration 0x2105..0x2108.

## Non-conclusions

- 0x2105 -> C064 is NOT proven.
- +0x12B is NOT simply CO number; C064 proves it is a broader object class/type field.
- Geometry/overlapping widgets are already understood and are not the analysis target.
- Old 0x08042146 -> 0x08038130 trace remains withdrawn.

## Continuation instruction

Continue from this note by attacking the missing C064 -> caller -> param_2 -> DAT_0803C218 boundary. Prefer structural/function-pointer evidence over naming guesses. If raw binary is unavailable, identify the exact Ghidra memory export needed to resolve DAT_0803C218 and the vtable/data words around the C064 dispatch path.
