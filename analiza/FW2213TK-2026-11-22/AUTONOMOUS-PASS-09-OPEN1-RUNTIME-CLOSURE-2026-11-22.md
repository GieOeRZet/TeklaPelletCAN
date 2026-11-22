# AUTONOMOUS PASS 09 — OPEN-1 RUNTIME CLOSURE / EMULATOR EVIDENCE — 2026-11-22

## Cel
Domknąć OPEN-1 oraz rozdzielić wcześniejszą analizę statyczną od późniejszego artefaktu emulatora, który zawiera wynik uruchomienia startupu firmware.

## Source / integralność
- FW2213TK_kopia.bin
- size 0x1F0000 = 2,031,616 B
- SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
- Unicorn ARM Cortex-M4
- image loaded at true 0x08010000
- reset vector 0x080A3209

## PASS 1 — D60 first runtime write
Runtime log: PC 0x0807E6CC -> [0x20008D60] <- 0x44.
Logged bytes are 44 45 0A 08, therefore little-endian value 0x080A4544.
STATUS: HARD runtime evidence.

## PASS 2 — D60 vtable
[0x20008D60] = 0x080A4544.
Corresponding PROJECT vtable = 0x08094544.
STATUS: HARD, contingent on supplied emulator result being reproduced from canonical BIN.

## PASS 3 — D60 slot 0
Vtable slot 0 = 0x0807E59D Thumb, physical function 0x0807E59C, PROJECT function 0x0806E59C.
This is the previously identified TX adapter.
STATUS: HARD.

## PASS 4 — node 4 object
Runtime log:
PC 0x0801FF46 -> [0x200114C0] = 0x20008D60
PC 0x0801FF48 -> [0x200114C4] = 0x20008D84
PC 0x0801FF4C -> [0x200114C8] = 4
Thus object[0] = D60 object, object[4] = parameter-record table, object[8] = node ID 4.
STATUS: HARD runtime evidence.

## PASS 5 — CAN poller object
Runtime log:
PC 0x080203FC -> [0x2002466C] = 0x080A4568
PC 0x080203FE -> [0x20024680] = 0x20008D60
PC 0x0802040E -> [0x20024684] = 0x20008D84
Therefore poller.vptr = 0x080A4568, poller.+0x14 = 0x20008D60, poller.+0x18 = 0x20008D84.
This closes the previously OPEN concrete object behind poller+0x14.
STATUS: HARD runtime evidence.

## PASS 6 — poller vtable
0x080A4568 slot0 -> 0x080729FD Thumb, PROJECT 0x080629FC.
Therefore poller -> 0x080629FC.
STATUS: HARD.

## PASS 7 — READ request
0x080629FC -> runtime record table -> parameter index -> 0x08062AE4 -> StdId 0x0604 -> command 0x40 -> BLX [poller+0x14].
With runtime closure: [poller+0x14] = 0x20008D60 and D60.vtable[0] = 0x0807E59D -> 0x0806E59C.
STATUS: HARD complete object path.

## PASS 8 — TX transport
0x0806E59C -> queue handle 0x200244EC -> 0x08057224 -> CanTxTask 0x080654A8 -> 0x08061734 -> CAN2 0x40006800.
Combined with PASS 7, the READ-request path is fully connected.
STATUS: HARD.

## PASS 9 — static-vs-runtime reconciliation
Earlier whole-BIN scan found zero direct LE32 occurrences of 0x20008D60 and 0x080A4544.
This is not a contradiction: the runtime result shows the object/vtable bytes are materialized during decompression/object initialization rather than appearing as a simple literal pointer.
The D60 bytes 44 45 0A 08 reconstruct to 0x080A4544.
Therefore D60 vptr changes from OPEN to HARD using the stronger runtime evidence.

## PASS 10 — remaining boundary
OPEN remains the local parameter write -> publication callback -> publication sink -> CAN 0x0584 command 0x42 bridge.
HARD already: FUN_0801117C detects/publishes tracked local changes; +0x7180 is the shared publication sink; wire contract is StdId 0x0584, DLC 8, command 0x42.
OPEN: concrete +0x7180 target, EstymaTask -> FUN_08010FCE route, full 260-slot parameter/CAN matrix.

## Net result
CLOSED: D60 runtime materialization; D60 vptr; D60 slot0; poller +0x14; poller +0x18; complete poller -> READ -> D60 -> TX adapter -> TX queue path.
OPEN: local-write -> publication callback; concrete +0x7180 implementation; EstymaTask scheduler route; full 260-slot parameter/CAN matrix; remaining UI/CAN object graphs.

## Evidence classification
HARD: runtime writes explicitly recorded by supplied emulator procedure/result.
HARD/STATIC: existing vtable and transport facts independently established from canonical BIN.
OPEN: anything not directly established by either source.

## Reproducibility condition
The emulator result is treated as evidence from the supplied source document. Full independent reproduction still requires the actual canonical BIN to be available to the execution environment.