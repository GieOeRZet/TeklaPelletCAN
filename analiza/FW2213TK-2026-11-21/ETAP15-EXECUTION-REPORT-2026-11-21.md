# TEKLAPELLET-CAN — ETAP 15 — EXECUTION REPORT
Data: 2026-11-21
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0
Firmware target: FW2213TK_kopia.bin
Firmware SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
decompiled.c blob: 9620d0c85259d34bb6a20d3b03b038945dfe4c1a

## 1. RAW EXPORT

### P1.1 — TX queue xrefs

[NEW-HARD] Direct Git-blob retrieval of decompiled.c was performed using blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a. Targeted scan of the complete recovered text found:
- literal text/hex 0x200244EC: 0 occurrences;
- literal text/hex 0x200244E0: 0 occurrences;
- FUN_080654A8 / FUN_0806E94C / FUN_0806E59C / FUN_08061734: 0 occurrences in this decompiled export;
- FUN_080617DC: 1 function definition.

[CONFIRMED-REPEAT] Existing Etap-14 BIN-derived evidence identifies:
- TX queue object: 0x200244E0;
- TX queue handle: 0x200244EC;
- CanTxTask entry: 0x080654A8;
- RX queue object: 0x200244BC;
- RX queue handle: 0x200244DC;
- CanRxTask entry: 0x0806E94C;
- one real TX producer: 0x0806E59C, in the 0x0604 path.

[NEW-HARD] The current decompiled export cannot independently enumerate producers of 0x200244EC because the producer/task bodies are outside the exported function set. Therefore the absence of 0x200244EC text in decompiled.c is NOT evidence that there are no producers.

[OPEN] Full all-producer xref list still requires raw BIN/Thumb xref or an already committed equivalent raw export.

### P1.2 — 20-byte CAN record: exact RX side

[NEW-HARD] FUN_080617DC is present in the recovered decompiled.c and gives an exact byte-level RX record layout:

| offset | size | source | meaning |
|---|---:|---|---|
| +0x00..+0x03 | 4 | RIR >> 21 when IDE=0 | StdId value |
| +0x04..+0x07 | 4 | RIR >> 3 when IDE=1 | ExtId value |
| +0x08 | 1 | RIR & 0x04 | IDE flag, stored as raw CAN register bit (0 or 4) |
| +0x09 | 1 | RIR & 0x02 | RTR flag, stored as raw CAN register bit (0 or 2) |
| +0x0A | 1 | RDTR & 0x0F | DLC |
| +0x0B..+0x0E | 4 | RDLR bytes 0..3 | Data[0..3] |
| +0x0F..+0x12 | 4 | RDHR bytes 0..3 | Data[4..7] |
| +0x13 | 1 | RDTR >> 8, low byte | RX metadata byte; on STM32 bxCAN register layout this position corresponds to the FMI byte, but the firmware itself only proves the copied byte, not a semantic name |

[NEW-HARD] The function also sets CAN interrupt/status flag bit 0x20 at CAN2 base +0x0C for mailbox 0, or +0x10 for mailbox 1/other selected mailbox path, after copying the record.

### P1.3 — TX layout

[CONFIRMED-REPEAT] Etap-14 raw/BIN evidence states FUN_08061734 consumes the same 20-byte TX record and directly programs CAN2 TIR, TDTR, TDLR, TDHR and TXRQ after checking CAN_TSR.

[OPEN] The exact TX-side assignments from FUN_08061734 are not present in the committed decompiled.c export. Therefore this report does not invent byte-level TX semantics beyond the proven common record shape from RX. The likely one-to-one mapping of +0x00/+0x04/+0x08/+0x09/+0x0A/+0x0B..+0x12 to TIR/TDTR/TDLR/TDHR remains to be confirmed from raw TX disassembly.

## 2. P2 — RX PARSER FUN_08063B80

[NEW-HARD] Targeted scan of the complete recovered decompiled.c found:
- no FUN_08063B80 definition;
- no 0x08063B80 marker;
- no 0x08062A40 / 0x08062AE4 / 0x08062B22 markers;
- functions.txt likewise has no FUN_08063B80 entry.

[CONFIRMED-REPEAT] Existing Etap-14 BIN-derived evidence still identifies the intended runtime chain:
CanRxTask 0x0806E94C -> FUN_08063B80 -> 0x08062A40 -> FUN_08062AE4 -> 0x08062B22 -> FUN_08011812.

[NEW-HARD] This establishes a source/export boundary: the Ghidra decompiled.c/functions.txt currently committed in the repo does not contain those named parser functions. It does NOT prove that the code is absent from firmware.

[OPEN] Full switch/branch map by CAN ID, including 0x580+node, 0x604, PDO/SDO/ACK and exact parser routing, requires raw BIN/Thumb disassembly or a committed parser raw export.

[OPEN] ACK/SDO semantics remain unclosed. No protocol semantics are inferred from CANopen naming alone.

## 3. P3 — RESOURCE TABLE DAT_0804866C

[NEW-HARD] FUN_080480C0 was recovered and its table access is exact:
- table symbol: DAT_0804866C;
- lookup compares signed halfwords at record offsets +0x00, +0x10, +0x20, +0x30 in each unrolled group;
- selected record index i is converted to i*0x10;
- selected fields used are +0x02, +0x04, +0x06, +0x07, +0x08 and +0x0C;
- +0x06 dispatches types 1,2,3,5;
- +0x07 is copied to widget+0x334;
- type 1 calls FUN_0804E598 and stores the returned/related pointer at widget+0x270;
- types 2 and 5 call FUN_0804E740(record+0x08, record+0x0C);
- type 3 calls FUN_0804E75A(record+0x08, record+0x0C);
- all entries finish through FUN_0804E5BC(widget,10).

[NEW-HARD] The recovered decompiled.c does not contain the literal bytes/values of DAT_0804866C itself. The table is referenced as a data symbol but not emitted as a data dump.

[CONFIRMED-REPEAT] The 23 Heating IDs requested are the two lists already recovered in reconstructed SRAM:
A9 AA BE B1 AF BC B4 B5 B6 B7 D3 D4
AD AE B0 B3 B2 B8 BA B9 BB BD CC

[OPEN] No committed raw dump of the 16-byte records at runtime 0x0804866C / raw offset 0x3866C is available in the current branch. Therefore no record values are fabricated here and no ID->TypedText/Bitmap/callback mapping is closed.

## 4. XREF / CALLGRAPH

### Transport
CanRxTask (0x0806E94C)
  -> RX queue 0x200244DC
  -> FUN_08063B80 [OPEN body]
  -> 0x08062A40 [OPEN body]
  -> FUN_08062AE4 [OPEN body]
  -> FUN_08062B22 [OPEN body]
  -> FUN_08011812
  -> parameter record +0x0C / local RAM

RX producer (0x0806F9F8)
  -> FUN_080617DC
  -> 20-byte RX record
  -> queue 0x200244DC

CanTxTask (0x080654A8)
  -> TX queue 0x200244EC
  -> FUN_08061734
  -> CAN2 0x40006800 mailbox registers

Known TX producer (0x0806E59C)
  -> queue 0x200244EC
  -> FUN_08057224 -> FUN_080574E4
  -> 0x0604 path

[OPEN] Other TX producers: not enumerated without raw xref.

### UI/resource
FUN_0803E714
  -> FUN_080480C0
  -> FUN_0804E4F8
  -> FUN_0804E598 / FUN_0804E740 / FUN_0804E75A
  -> FUN_0804E5BC
  -> FUN_08032316
  -> vtable slot +0x10 / update path

CO1..CO4 list selection
  -> common 12-ID list
  -> FUN_08036FF2
  -> FUN_0804842C
  -> widget base +0x42C + N*0x338
  -> resource dispatch

## 5. INTERPRETATION

[NEW-STRONG] The 20-byte record is not a generic opaque queue item. RX construction proves it is a compact firmware-owned CAN frame structure with explicit ID mode, RTR, DLC, 8 data bytes and one extra RX metadata byte. This is sufficient to define the RX-side software structure for the future ESP32-C6 implementation.

[NEW-STRONG] The +0x08 and +0x09 fields preserve the bxCAN register bit values (4 and 2), not normalized booleans. A 1:1 emulator should preserve this representation unless TX-side evidence proves normalization before TIR construction.

[NEW-STRONG] The parameter write path and CAN TX producer path are distinct subsystems. FUN_08011812 only updates the parameter record/local storage; the missing link is a separate producer/serialization path that must be recovered before claiming UI parameter changes are transmitted over CAN.

[OPEN] It is still not proven that every local parameter write is immediately serialized to CAN. The project must not implement such behavior until a producer/caller is identified.

[OPEN] The resource table semantics are structurally known but its literal records are not. Therefore exact CO1..CO4 widget/resource mapping remains open.

## 6. STATUS

| Item | Status |
|---|---|
| RX 20-byte record layout | [NEW-HARD] |
| RX mailbox extraction | [CONFIRMED-REPEAT] + [NEW-HARD] exact field map |
| TX queue addresses | [CONFIRMED-REPEAT] |
| Known TX producer 0x0806E59C | [CONFIRMED-REPEAT] |
| All TX producers | [OPEN] |
| FUN_08061734 exact body | [OPEN] |
| FUN_08063B80 exact body | [OPEN] |
| CAN ID routing / ACK / SDO | [OPEN] |
| DAT_0804866C table pointer/value dump | [OPEN] |
| 23 Heating resource records | [OPEN] |
| CO1..CO4 -> widget -> TypedText/Bitmap/callback | [OPEN] |
| Parameter RAM writer 0x11812 | [CONFIRMED-REPEAT] |
| Parameter write -> CAN TX serialization | [OPEN] |

## 7. SOURCE LIMIT / NEXT RAW REQUIREMENT

The remaining closures are not blocked by reasoning; they are blocked by missing raw material in the current branch:
1. raw Thumb for 0x080654A8 / 0x0806E94C / 0x0806E59C / FUN_08061734;
2. raw Thumb/xrefs for 0x08063B80 and 0x08062A40/AE4/B22;
3. raw data dump around runtime 0x0804866C (raw 0x3866C) covering the resource records;
4. if necessary, RAM/init dump for 0x20005EF0..0x20005F5B.

No guessed values were inserted.
