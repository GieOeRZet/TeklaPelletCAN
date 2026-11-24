# AUTONOMOUS PASS 20 — LOCAL WRITE -> PUBLICATION -> CAN TX BRIDGE — 2026-11-22

## NEW-HARD — local parameter write

FUN_08011812 performs range validation and, on success, writes the new value into the runtime record's local storage pointer at record +0x0C.

At the final write block:
- type 1 -> byte store
- type 2 -> halfword store
- type 3 -> word store
- type 4 -> halfword store
- type 5 -> word store

Return 0x0 confirms the local write path succeeded.

## NEW-HARD — publication scanner

FUN_0801117C is the outbound local-change/publication engine.

It:
- scans the runtime table with stride 0x2C;
- skips special PIDs 0x2165 and 0x3726..0x372? family shown in the branch set 0x2311..0x2314;
- obtains the current typed value through FUN_080115F6;
- compares it with a shadow/publication value;
- when different, stores the new shadow value and publishes;
- uses manager field +0x7180;
- invokes publication sink vtable slot 0.

The publication frame is assembled with:
- StdId 0x0584;
- DLC 8;
- command 0x42;
- PID little-endian;
- type byte;
- value encoded according to the parameter type.

## NEW-HARD — concrete publication sink

+0x7180 = object 0x20008D60.
Runtime vptr = 0x080A4544, PROJECT = 0x08094544, RAW = 0x94544.
Vtable slot 0 = runtime 0x0807E59D / PROJECT 0x0806E59D / physical FUN_0806E59C.

FUN_0806E59C:
- copies the publication record into a local TX record;
- obtains queue 0x200244EC;
- calls queue primitive 0x08057224;
- this feeds the established CanTxTask -> CAN2 transport.

## CLOSED combined bridge

local/UI write
-> FUN_08011812
-> runtime record +0x0C
-> FUN_0801117C change detection
-> frame StdId 0x0584 / command 0x42
-> [manager+0x7180] = 0x20008D60
-> vtable slot 0 = FUN_0806E59C
-> queue 0x200244EC
-> CanTxTask
-> CAN2

This closes the previously open machine-level local-write -> outbound CAN publication bridge.

## Remaining semantic boundary

Still OPEN:
1. Exact conditions/timing that invoke FUN_0801117C from FUN_08010FCE.
2. Complete shadow/publication table semantics.
3. Complete 260 catalog -> runtime PID -> CAN mapping.
4. Provider persistence semantics.
5. Sidecar class 1/2/3 semantic differences.

Evidence: canonical BIN SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071.