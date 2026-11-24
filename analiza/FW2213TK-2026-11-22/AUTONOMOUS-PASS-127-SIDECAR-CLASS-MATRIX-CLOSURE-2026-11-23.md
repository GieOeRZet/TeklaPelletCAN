# AUTONOMOUS PASS 127 — SIDECAR CLASS MATRIX CLOSURE — 2026-11-23

## Objective
Reconcile all current hard evidence for the registration/state byte at physical R(i)+0x2C and separate proven behavior from business-semantic naming.

## HARD matrix

| Sidecar value | Guarded write in FUN_08011812 | Provider sync in FUN_08011368 | Static direct registration evidence | Current status |
|---:|---|---|---|---|
| 0 | not accepted when guarded | not selected | none established | live/non-sync family from runtime matrix; exact business naming already documented as live |
| 1 | **accepted** | not selected | no direct FUN_0801143C caller with 1 recovered | **write-authorized / command-like behavior HARD** |
| 2 | **rejected** by guarded-write check (status 9) | **selected** | no direct static registration with 2 recovered | **sync-only class HARD** |
| 3 | **accepted** | **selected** | PID 0x3500, 0x3502, 0x350B all register with 3 | **write-authorized + sync class HARD** |
| other nonzero | rejected by guarded-write check | not selected by the 2/3 sync branch | no evidence | unsupported by these paths |

## HARD execution facts

### Guarded write
FUN_08011812 reads R(i)+0x2C when its param_5 != 0 gate is active and accepts only values 1 or 3. Other values fail that gate.

### Provider synchronization
FUN_08011368 scans the same 0x2C-stride record space and selects only sidecar values 2 or 3. For selected records it: reads PID/value/type; calls provider getter through manager+0x7178; compares provider/local using the runtime type; on mismatch/error calls provider slot +0x04 with local value/type.

### Registration
FUN_0801143C stores R(i)+0x2C = param_10 and R(i)+0x30 = param_9. The three recovered direct registration call sites all use param_10=3: PID 0x3500 (Main module type), PID 0x3502 (CH expansion module type), PID 0x350B (Profile number). The static export does not prove that dynamic registrations never use class 2 or 1.

## Reconciled semantic model
The byte is not merely an access flag. It is a registration/state class whose proven machine behavior is: 1 permits guarded parameter writes but is outside the dedicated provider-sync scan; 2 participates in provider synchronization but is not accepted by the guarded-write gate; 3 participates in both provider synchronization and guarded writes.

The labels command/mirror/setting are used only where independently backed by the existing runtime PID matrix; they are not used here to infer undocumented business behavior.

## Boundary
This closes the machine-level class matrix for the two generic mechanisms that inspect R+0x2C. It does not identify every dynamic registration caller or prove that every parameter in the same class has identical business semantics.

Next: complete 260/catalog cross-layer correlation; exact raw CFG for provider slot4 target 0x080617FF; remaining UI classes 11/13/15/18/19/20; R+0x00..+0x07 and R+0x0A; dynamic-only B1/B2 remain with Claude.