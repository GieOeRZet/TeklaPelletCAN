# NewEstyma — PARAMETER SIDECAR / SYNC CLOSURE 05 — 2026-11-22

Primary source: complete Ghidra decompilation blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a.

## New HARD findings

### 1. Registration is physically organized as four records per 0xB0 block

FUN_0801143C scans R(i)+0x08, R(i+1)+0x08, R(i+2)+0x08 and R(i+3)+0x08, then advances the base pointer by 0x58 ushort units = 0xB0 bytes. This is an optimization/scan grouping. It does NOT change the canonical record stride, which remains 0x2C.

### 2. +0x2C is an active side-car/state byte

FUN_0801143C writes R(i)+0x2C = (byte)param_10 and R(i)+0x30 = param_9. Because canonical stride is 0x2C, these addresses are the prefix of R(i+1).

FUN_08011812 reads R(i)+0x2C when param_5 != 0 and accepts only 1 or 3; otherwise it returns status 9. Therefore the adjacent byte is an active operation/state gate, not padding.

### 3. Side-car value 2/3 drives a separate synchronization pass

FUN_08011368 scans the same 0x2C records and reads R(i)+0x2C. Only side-car values 2 and 3 enter its synchronization path.

For those records it reads PID from R+0x08, reads current value/type through FUN_080115F6, calls an object at object+0x7178 with PID and a value buffer, resolves the destination type, and if the externally obtained value differs from the local value, calls the object's vtable slot +4 to update it.

This proves values 2/3 belong to a distinct synchronization/update class.

### 4. Direct registration callers currently recovered all use param_10 = 3

The complete decompilation blob contains three direct calls to FUN_0801143C:

- PID 0x3500, Main module type
- PID 0x3502, CH expansion module type
- PID 0x350B, Profile number

All three pass param_10 = 3.

The calls also pass param_9 as a string pointer in the first two cases and as 1 in the profile-number case.

This is direct evidence that class/state 3 is used by module/profile-related registrations. It is NOT yet proof that every parameter with side-car 3 belongs to the same semantic subsystem.

### 5. Side-car value 1 is the write-authorization class used by FUN_08011812

FUN_08011812's optional side-car check accepts only 1 or 3.

Hard model so far:
- side-car 1: accepted by guarded writes
- side-car 3: accepted by guarded writes and participates in the dedicated sync pass
- side-car 2: participates in the dedicated sync pass but is rejected by the guarded-write check
- other nonzero values: rejected by that guarded-write check

The exact business meaning of 1/2/3 remains OPEN.

### 6. Parameter publication path is directly visible in FUN_0801117C

FUN_0801117C scans records, watches a specific set of PIDs (0x2165, 0x3726, 0x2311..0x2314 exclusions), and when a tracked value changes it constructs:
- StdId 0x0584
- DLC 8
- data command 0x42
- PID in the payload
- current value encoded according to the record type

and invokes the object's function at object+0x7180.

This is a concrete local-change -> CAN publication path, distinct from the generic WRITE path.

## Important refinement

The previous description "side-car/access gate" was too narrow. The hard evidence now shows that the byte at physical R(i)+0x2C is a registration/state class byte used by at least two independent mechanisms: guarded parameter writes (FUN_08011812) and module/profile synchronization (FUN_08011368).

Its exact semantic names remain intentionally OPEN.

## Remaining high-value targets

1. Identify all indirect registration callers and recover their param_10 classes.
2. Resolve object +0x7178 and +0x7180 vtables to close the synchronization/publication graph.
3. Enumerate all PIDs entering FUN_0801117C's publication filter.
4. Connect the three direct 0x3500/0x3502/0x350B registrations to the 260 catalog and UI.
5. Resolve the meaning of R+0x0A and R+0x00..+0x07 without guessing.
