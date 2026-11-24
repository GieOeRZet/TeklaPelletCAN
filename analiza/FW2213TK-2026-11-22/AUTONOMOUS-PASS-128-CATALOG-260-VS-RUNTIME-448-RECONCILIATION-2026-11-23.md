# AUTONOMOUS PASS 128 — 260-CATALOG VS RUNTIME-448 RECONCILIATION — 2026-11-23

## Objective
Resolve an important terminology collision before building the cross-layer matrix.

## HARD current evidence

### 260-slot catalog
The older static analysis identifies a distinct 260-slot catalog around RAW `0x037578`:
- 260 catalog slots;
- 260 unique catalog parameter IDs;
- 247 slots have an init caller through `FUN_0801143C`;
- 11 have direct init through `FUN_08014700`;
- 248 have at least one of those mechanisms;
- 12 have neither in the recovered static caller inventory.

This is a real static catalog claim and remains a valid target for the requested 260-row matrix.

### Runtime parameter table
Startup emulation independently recovered:
- 655 populated runtime records at manager `0x20008D84`;
- canonical stride `0x2C`;
- runtime key = PID;
- 448/448 panel-catalog PIDs are present in the runtime table with matching names.

### UI resolver tables
`FUN_08036FF2` has two separate resolver tables:
- table 1: RAW `0x37B48`, 49 CH family records;
- table 2: RAW `0x37578`, 372 singleton records, PID in the table.

The 372-record resolver table is therefore **not** the 260-slot catalog merely because both use the same general PID-resolution area.

## Reconciled model

The project currently contains at least these distinct parameter universes:

1. **260-slot static catalog** — historical/static catalog target around the earlier catalog analysis.
2. **49 CH family resolver positions** — instance-aware mapper.
3. **372 singleton resolver positions** — direct-PID mapper.
4. **448 panel catalog PIDs** — catalog coverage proven in the 655-record startup runtime.
5. **655 populated runtime records** — emulator-recovered manager table.
6. **660 lookup/search bound** — maximum scan space, not populated-count proof.

Do not collapse these counts.

## Immediate consequence

The previous wording "260 catalog = complete panel PID catalog" is too strong. The current evidence proves the 260 catalog as a distinct static layer and separately proves 448 panel-catalog PIDs in the 655-record runtime.

The open matrix task must therefore explicitly map:
`260 static catalog -> PID -> 655 runtime record (where present) -> 49/372 resolver position(s) -> provider/CAN/UI`

with absence/non-overlap recorded rather than silently treating counts as equal.

## Next

1. Extract the 260 catalog rows directly from the source artifact used by the 260-slot analysis.
2. Join them against `runtime_param_table_655.csv` by PID.
3. Join resolver T1/T2 and `pid_matrix_655.csv`.
4. Record exact coverage and missing joins.
