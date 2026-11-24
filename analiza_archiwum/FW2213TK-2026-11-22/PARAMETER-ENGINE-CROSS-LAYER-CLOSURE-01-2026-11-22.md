# PARAMETER ENGINE — CROSS-LAYER CLOSURE 01 — 2026-11-22

## Result

Three layers must be kept separate:

1. 260-slot catalog.
2. UI/module mapper: 49 family-of-four groups + 0x174 = 372 singleton positions = 568 logical mapper positions.
3. Runtime parameter-record engine at 0x20008D84 with a 0x2C stride and a hard lookup scan bound of 0x294 = 660 positions.

Architecture:

UI/internal index -> FUN_08036FF2 -> family/singleton mapper -> external parameter ID -> FUN_08037094/FUN_080370C0 -> FUN_080115F6 -> runtime record -> typed storage/UI/CAN.

## Major correction

The old statement `record +0x2C = access/flag` and `record +0x30 = metadata` is incompatible with the proven 0x2C record stride.

For record[n] = 0x20008D84 + n*0x2C:
- +0x2C is the beginning of record[n+1].
- +0x30 is +0x04 inside record[n+1].

Therefore those two old field assignments are REJECTED as fields of the same 0x2C record.

This does not invalidate the independently supported +0x08, +0x0C, +0x10, +0x14, +0x1C and +0x24 accesses.

## Current record model

| Offset | Status | Role |
|---:|---|---|
| +0x00..+0x07 | OPEN | unknown |
| +0x08 | HARD | 16-bit external/CAN parameter ID used by lookup |
| +0x0A | OPEN | unknown |
| +0x0C | HARD | pointer to value storage; dereference yields current value |
| +0x10 | HARD | 8-bit type tag |
| +0x11..+0x13 | OPEN | unknown |
| +0x14 | STRONG/HARD path | field returned by FUN_0801167A |
| +0x18..+0x1B | OPEN | unknown |
| +0x1C | STRONG/HARD path | field returned by FUN_080116E6 |
| +0x20..+0x23 | OPEN | unknown |
| +0x24..+0x27 | STRONG | metadata field from existing record-engine analysis |
| +0x28..+0x2B | OPEN | unknown |
| +0x2C | boundary | next record |

## Why 260, 568 and 660 are not contradictory

260 is a catalog cardinality.

568 is the logical UI/model mapper namespace: 49*4 family positions plus 372 singleton positions.

660 is the maximum runtime lookup scan extent observed in FUN_080115F6. It is NOT proof that 660 records are populated.

The runtime lookup is ID-based: record +0x08 is compared against the requested parameter ID. Therefore mapper position, catalog slot and runtime record position are distinct concepts.

## Instance model

For family-of-four parameters:

internal index -> family base -> base + instance - 1 -> external PID

with instance from object +0x12C.

This is the correct generic model for CO1..CO4. Do not implement four independent parameter databases.

## Convergence

UI READ:
internal index -> FUN_08036FF2 -> FUN_08037094 -> FUN_080115F6 -> record +0x0C.

UI WRITE:
UI -> FUN_08037212 -> FUN_08011812 -> record +0x0C.

CAN WRITE:
CAN RX -> FUN_08062B22 -> FUN_080115F6 -> type -> FUN_08011812 -> record +0x0C.

The runtime record engine is therefore the common parameter-state layer, not a UI-only structure.

## Next macro pass

Do not spend another pass expanding the 260 catalog.

Priority:
1. Resolve every remaining field of the 44-byte record.
2. Recover all arguments written by FUN_0801143C.
3. Build caller -> PID -> storage -> type -> record-field matrix.
4. Cross-link all 568 mapper positions to external PID and runtime record.
5. Then connect the resulting parameter graph to CAN publication/TX and UI bindings.

## Status

[CLOSED/HARD] 260-slot catalog is separate.
[CLOSED/HARD] mapper = 49 family-of-four groups + 372 singleton positions.
[CLOSED/HARD] runtime stride = 0x2C.
[CLOSED/HARD] runtime base = 0x20008D84.
[CLOSED/HARD] lookup scan bound = 660 positions.
[CLOSED/HARD] +0x08 PID, +0x0C storage pointer, +0x10 type.
[REJECTED] +0x2C as a field of the same record.
[REJECTED] +0x30 as a field of the same record.
[OPEN] populated count, complete field map, registration semantics, mapper-to-record mapping, complete CAN mapping.