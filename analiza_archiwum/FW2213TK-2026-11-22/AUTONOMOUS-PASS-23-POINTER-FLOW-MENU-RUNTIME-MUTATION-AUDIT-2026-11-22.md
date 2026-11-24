# AUTONOMOUS PASS 23 — POINTER FLOW / MENU RUNTIME TABLE MUTATION AUDIT — 2026-11-22

## Objective

Remove the current bottleneck around the two reconstructed MenuTree runtime tables:

- SRAM 0x20005EF0 — runtime class table
- SRAM 0x20005F08 — access/update table

The previous passes proved their initial contents and found only one direct LE32 pointer literal for each. This pass follows the next layer: Thumb PC-relative LDR literal -> literal-pool word -> SRAM target -> same-function memory access.

## Tool added

- tools/pointer_flow_scan.py
- tools/test_pointer_flow_scan.py

The scanner is deliberately evidence-first. It currently decodes:
- Thumb 16-bit PC-relative LDR literal;
- literal-pool dereference;
- common 16-bit Thumb load/store forms;
- basic tracked-register lifetime;
- common Thumb function epilogues.

It reports candidate/static flow only. It does not promote semantic meaning.

## Canonical firmware

SHA-256:
1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Size:
0x1F0000

Address rule:
RUNTIME = PROJECT + 0x10000
PROJECT = RAW + 0x08000000

## HARD observations

### 1. Runtime class table 0x20005EF0 has two code materializations

The same literal-pool word at RAW 0x3C218 contains:
0x20005EF0

It is reached by two Thumb LDR-literal instructions:

| LDR RAW | PROJECT | Register | Pool RAW |
|---:|---:|---|---:|
| 0x3C068 | 0x0804C068 | r0 | 0x3C218 |
| 0x3C17A | 0x0804C17A | r2 | 0x3C218 |

Function candidates are respectively PROJECT 0x0803C064 and 0x0803C178.

### 2. First 0x20005EF0 consumer performs indexed byte access

At RAW 0x3C06A the instruction is the Thumb register-offset LDRB form using r0 as base and r1 as index.

This is direct evidence that the SRAM table is consumed as a byte-indexed array, not merely copied as a scalar.

The load writes its result into r0, so pointer tracking is terminated immediately after that access. Later r0-relative operations in the function are therefore not promoted as accesses to 0x20005EF0.

### 3. Second 0x20005EF0 consumer performs indexed read and byte write

Function candidate PROJECT 0x0803C178 materializes the same table into r2.

At RAW 0x3C17C:
- LDRB using r2 as base and r1 as index.

At RAW 0x3C1FE:
- STRB using r2 as base with immediate offset 6.

Because r2 is not overwritten between these operations, both accesses retain a valid pointer provenance to 0x20005EF0.

The second access is therefore a concrete static write into the runtime class table at:
0x20005EF0 + 6

This is the first direct static evidence found in this workflow of a later mutation of one of the 21 runtime class bytes.

### 4. Access/update table 0x20005F08 has one materialization and a direct read

Literal pool:
- RAW 0x42314 contains 0x20005F08.

LDR literal:
- RAW 0x422CE
- PROJECT 0x080522CE
- loaded register r5.

Function candidate:
- PROJECT 0x080522C8.

At RAW 0x422DE there is an LDRB using r5 as the base with zero immediate offset.

This is direct evidence that 0x20005F08 is consumed byte-wise from the materialized pointer.

The scanner stops at the function epilogue and does not incorrectly attribute later functions to this pointer.

## Important negative result

A raw LE32 literal search alone was insufficient to recover these consumers:
- 0x20005EF0 has one literal-pool occurrence but two code materializations.
- 0x20005F08 has one literal-pool occurrence and one recovered code materialization.

Therefore the previous conclusion that the producer/use graph was hidden behind only one literal anchor was incomplete, not wrong. The missing layer is pointer provenance through literal pools.

## What remains OPEN

- Exact semantic meaning of the write at 0x20005EF0+6.
- Whether other writes to 0x20005EF0 are generated through MOVW/MOVT, address arithmetic, aliases, or calls.
- Complete write/read enumeration for all 21 indices.
- Later mutations of 0x20005F08.
- Exact relation between runtime class mutation and screen/page-family selection.
- Exact relation between access/update table mutation and guarded write/update behavior.
- Row callback and widget/resource graph.
- Full PID -> UI -> CAN matrix.

## Rejected interpretation

Do not interpret the 0x20005EF0 + 6 write as a business-semantic assignment yet. The static proof establishes address provenance and byte-store mechanics only.

## Next attack

1. Extend pointer-flow scanning to MOVW/MOVT materialization and pointer arithmetic.
2. Enumerate every operation that can write into both 21-byte tables.
3. Correlate table indices with the 21 MenuTree rows.
4. Trace the write at +6 backwards to its source value and condition.
5. Trace the table read forward into the page/visibility resolver.
6. Continue toward the complete screen/widget/PID/CAN matrix.

## Evidence status

- Pointer materialization for 0x20005EF0: HARD
- 0x20005EF0 indexed read: HARD
- 0x20005EF0 +6 byte write: HARD as machine-level address operation
- Pointer materialization for 0x20005F08: HARD
- 0x20005F08 byte read: HARD
- Business meaning of +6: OPEN
- Complete mutation graph: OPEN
