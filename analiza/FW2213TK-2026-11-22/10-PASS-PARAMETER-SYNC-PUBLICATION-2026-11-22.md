# 10-pass closure — parameter sync/publication / Estyma task
Date: 2026-11-22

## Pass 1 — +0x7178 / +0x7180 concrete writes
[HARD] Full decompilation blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a contains only call sites for offsets +0x7178 and +0x7180.
No direct assignment/store to either field was recovered in the decompiled C.
Therefore the concrete provider/publication implementation remains OPEN; no vtable target is guessed.

## Pass 2 — scheduler boundary
[HARD] \`FUN_08010fce\` is the only direct function-body occurrence/caller-visible reference to the sync/publication chain in the decompilation text, and it calls:
1. \`FUN_08011368\` provider synchronization,
2. \`FUN_0801117c\` local-change publication,
3. periodic publication logic.
No direct C caller of \`FUN_08010fce\` is present in the blob, so its task/dispatch entry is likely installed indirectly. This is OPEN at scheduler-registration level.

## Pass 3 — periodic publication cadence
[HARD] \`FUN_08010fce\` gates its slow publication path by \`*DAT_080119f8 % 10 == 0\`.
It then uses object byte \`param_1+0x717d\` as a warm-up counter:
- increments until >30,
- only then performs the indexed publication,
- after publication advances \`DAT_08011a00[0]\` through 0..0x293.
Thus the chain contains a delayed start plus a round-robin scan over the 660-record address space.

## Pass 4 — static registration classes
[HARD] Exactly three direct \`FUN_0801143c\` registration call sites are present in the decompilation:
- PID 0x3500, sidecar/class argument param_10 = 3
- PID 0x3502, param_10 = 3
- PID 0x350B, param_10 = 3
These are Main module type, CH expansion module type, Profile number.
This does NOT prove that dynamic registrations never use class 2; it proves the three statically visible registrations use class 3.

## Pass 5 — \`FUN_0801100c\` is a type-aware out-of-range detector
[HARD] \`FUN_0801100c\` scans records, but only sidecar classes 2/3 (\`R+0x2C\`).
For each candidate it:
- resolves the current local value by runtime type,
- reads a second value from the record/descriptor path,
- compares them with signed-aware semantics,
- returns the PID of the first mismatch.
\`FUN_0801113a\` repeatedly calls it and repairs the returned PID through \`FUN_08011812(..., param_5=0,param_6=1)\` using the record default descriptor.
This strengthens the separation:
- class 2/3 records participate in synchronization/validation,
- default repair is a distinct path from provider publication.

## Pass 6 — local-change publication contract
[HARD] \`FUN_0801117c\` scans the same 0x2C record table and tracks PIDs:
0x2165, 0x3726, 0x2311, 0x2312, 0x2313, 0x2314.
For changed tracked values it emits:
- StdId 0x0584
- DLC 8
- command 0x42
- PID in bytes 0..1 of payload structure
- value encoded according to resolved runtime type.
It limits the number of changes published in one scan to six (\`bVar6\`), then marks the scan state complete.
This is a hard publication contract independent of +0x7180's concrete implementation.

## Pass 7 — publication is used from two distinct paths
[HARD] +0x7180 is called from both:
- \`FUN_0801117c\` (tracked local-value changes),
- \`FUN_08010fce\` (round-robin periodic publication).
Therefore +0x7180 is not merely a one-shot UI callback; it is a shared outbound publication sink.

## Pass 8 — initialization-time provider sync
[HARD] \`FUN_0801143c\` performs an immediate provider getter for sidecar classes 2/3.
If getter succeeds:
- the provider result is converted to the registered runtime type,
- for type 4 signed-16 is preserved,
- otherwise the value is normalized to type 3 for the local write,
- \`FUN_08011812\` commits the value.
Thus provider synchronization is performed already during registration, not only by the periodic loop.

## Pass 9 — periodic provider sync and write-back
[HARD] \`FUN_08011368\` scans at most 11 records per invocation (\`iVar7\` starts at 11 and decrements).
It selects only sidecar 2/3 records and calls the +0x7178 getter with:
\`(provider, PID, destination 5-byte descriptor)\`.
If getter succeeds, it compares provider vs local using the resolved runtime type.
On mismatch/error it calls provider vtable slot +4 with:
\`(provider, PID, local_value, runtime_type)\`.
This establishes the provider interface as a bidirectional synchronization API:
- slot 0: GET(PID, descriptor_out) -> status
- slot +4: SET(PID, value, type) -> status/ignored result

## Pass 10 — Estyma task spine
[HARD] \`FUN_08062d82\` creates the FreeRTOS tasks:
- GUITask
- EstymaTask
- CanRxTask
- CanTxTask
The \`FUN_08010fce\` scheduler caller is not exposed as a direct call in the decompiled blob. Therefore the remaining closure target is to recover the EstymaTask entry/dispatch chain and locate how \`FUN_08010fce\` is reached.

## Consolidated result
The parameter subsystem is now closed at three executable layers:

1. RECORD ENGINE
   PID + storage + runtime type + min + max + default + sidecar state.

2. PROVIDER SYNCHRONIZATION
   +0x7178 interface:
   GET(PID, 5-byte descriptor)
   SET(PID, value, type)
   used at registration and periodically for sidecar 2/3.

3. CAN PUBLICATION
   +0x7180 sink:
   shared outbound path for tracked local changes and periodic round-robin publication.
   Wire contract is StdId 0x0584 / DLC 8 / command 0x42 with PID/value encoding.

Still OPEN:
- concrete object/vtable target behind +0x7178,
- concrete publication target behind +0x7180,
- exact indirect scheduler route to \`FUN_08010fce\`,
- full semantics of sidecar class 2 vs class 3,
- full semantics of \`FUN_0801100c\`'s second comparison source.

No rejected hypothesis was revived.
