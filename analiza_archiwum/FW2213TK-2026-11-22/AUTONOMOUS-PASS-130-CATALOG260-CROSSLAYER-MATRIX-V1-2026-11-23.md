# AUTONOMOUS PASS 130 — 260 CATALOG CROSS-LAYER MATRIX V1 — 2026-11-23

## Artifact
analiza_archiwum/FW2213TK-2026-11-22/data/catalog260_crosslayer_matrix_v1.csv

Exactly 260 rows.

## Added hard-derived columns

### provider_get_set
YES when the joined runtime sidecar class is 2 or 3, because FUN_08011368 selects exactly those classes and uses provider GET/SET.

### guarded_write
YES when the joined runtime sidecar class is 1 or 3, because FUN_08011812's guarded sidecar check accepts exactly 1 or 3.

### ui_resolver_row
YES for the 252 runtime-present catalog rows. The 260 catalog is the first 260 rows of resolver_t2; the eight catalog rows with in_runtime=0 are retained as negative rows.

### direct_0584_42_tracked
YES only for catalog PID 0x3726 among the six hard-coded local-change publication PIDs:
0x2165, 0x3726, 0x2311, 0x2312, 0x2313, 0x2314.

For this 260-row catalog subset:
- provider GET/SET eligible: 153 rows (all class 3; class 2 has 0 rows here)
- guarded-write eligible: 175 rows (class 1 + class 3)
- runtime/UI-resolver present: 252 rows
- direct 0x0584/0x42 tracked: 1 row (PID 0x3726)

## Important boundary

The absence of direct 0x0584/0x42 tracking does NOT mean a PID can never be emitted by the periodic round-robin publication path. The six-PID list is specifically the hard local-change publication filter in FUN_0801117C.

Likewise provider eligibility is a generic sidecar-class result, not proof of a PID-specific business subsystem.

Next matrix layer:
- exact CAN RX/RD parser relation for every runtime PID;
- exact periodic publication decision at each runtime record;
- UI presenter/resource/widget binding where direct evidence exists;
- persistence/provider concrete implementation;
- remaining UI classes and raw CFG gaps.
