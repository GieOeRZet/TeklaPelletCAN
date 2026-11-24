# AUTONOMOUS PASS 129 — 260 CATALOG -> RUNTIME MATRIX 01 — 2026-11-23

## Objective
Turn the established 260-slot catalog into an explicit row-by-row join against the 655-record runtime matrix.

## HARD result

The 260 catalog occupies the first 260 rows of the recovered resolver table at RAW 0x37578:
- catalog indices 0..259;
- row 259 at RAW 0x37984;
- next row starts at RAW 0x37988 with resolver index 260, outside the 260-slot catalog.

The generated artifact is:
analiza_archiwum/FW2213TK-2026-11-22/data/catalog260_runtime_matrix.csv

It contains exactly 260 rows and joins:
- catalog index/raw offset/UI key/PID/name;
- resolver in_runtime flag;
- runtime type/min/max/default;
- storage/config offset;
- sidecar class/mode/write/sync;
- known UI keys.

## Coverage

- 260 unique catalog PIDs.
- 252/260 have in_runtime=1 and a matching PID row in pid_matrix_655.csv.
- 8/260 are explicitly absent from the 655-row runtime matrix:
  - UI 0x002C -> PID 0x211A
  - UI 0x0049 -> PID 0x3002
  - UI 0x0074 -> PID 0x2269
  - UI 0x0081 -> PID 0x228E
  - UI 0x0082 -> PID 0x228F
  - UI 0x0095 -> PID 0x218B
  - UI 0x0096 -> PID 0x218C
  - UI 0x0080 -> PID 0x228D

These eight are not missing from the catalog; they are catalog rows whose runtime flag is 0.

Named catalog rows: 245/260. The remaining unnamed rows are still valid catalog slots/PIDs; blank names are not treated as absence.

## Runtime sidecar distribution for the 252 joined rows

- class 0: 77
- class 1: 22
- class 3: 153
- class 2: 0 in this 260-row joined subset.

This is a property of the current catalog subset, not a claim that class 2 does not exist elsewhere in the 655-record runtime universe.

## What is now CLOSED

The 260 catalog is no longer only a count claim. Each of its 260 rows has an explicit row-level artifact, with runtime join status and the available runtime metadata.

The matrix can now be extended without re-discovering the catalog boundary.

## Still OPEN

For each of the 252 runtime-present rows, exact provider GET/SET use, publication participation, CAN RX/TX frame mapping, and UI widget/resource binding are not all proven. The next matrix layers must add those fields from direct evidence.

The 8 runtime-absent catalog rows must remain explicit negative rows rather than being forced into runtime records.
