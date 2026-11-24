# NewEstyma — PARAMETER ↔ CAN GRAPH ATTACK 01 — 2026-11-22

## 1. Canonical parameter anchor

Node:
0x20008D84

Parameter engine:
- resolver: 0x08010FC2
- type getter: 0x08014734
- type writers: 0x08014700 / 08 / 10 / 18 / 20
- 0x080115F6: 0x2C-stride parameter-table operations
- 0x08011812: parameter update/commit
- 0x08062B22: CAN parameter parser

## 2. 260-slot catalog — HARD

Around RAW 0x037578:
- 260 unique slots
- 260 unique parameter IDs
- no duplicate parameter IDs
- no duplicate slots

This catalog is an index/accelerator and must not be equated with every parameter existing in firmware.

## 3. CAN READ graph — CLOSED/STRONG

Runtime read scheduler:

0x080629FC
 -> runtime parameter table
 -> base + counter*0x2C + 0x08
 -> parameter index
 -> 0x08062AE4
 -> CAN frame StdId 0x0604, command 0x40
 -> indirect dispatch [obj+0x14]
 -> vtable family containing 0x0806E59C
 -> 0x200244EC / CanMessagesToTransmit
 -> 0x08057224
 -> CanTxTask
 -> 0x08061734
 -> CAN2

The dispatch-table evidence:
0x08094508 slot 5 -> 0x0806E59C
0x08094508 slot 8 -> 0x080629FC

Exact assignment of [obj+0x14] to this vtable remains OPEN.

## 4. CAN WRITE / RX parameter graph — CLOSED

CAN2 RX
 -> 0x080617DC
 -> ReceivedCanMessages
 -> CanRxTask
 -> 0x08063B80
 -> 0x08062A90
 -> StdId 0x0584
 -> data[3]>>5 == 2
 -> 0x08062B22
 -> parameter ID = frame[4] | frame[5]<<8
 -> resolver/type decode
 -> 0x08011812
 -> parameter record +0x0C / local RAM

0x08062B22 has explicit type branches 1..5.

Special indices:
0x3722 / 0x3723 receive special handling before ordinary type decode.

## 5. UI WRITE graph — CLOSED only to local RAM

UI
 -> 0x08037212
 -> 0x08011812
 -> parameter record +0x0C
 -> local parameter RAM

0x08037212 has 33 UI callers.

0x08011812 is NOT proven to trigger CAN TX.

## 6. Catalog -> CAN mapping

The current hard graph proves the following shared middle layer:

parameter ID
 -> parameter record / descriptor
 -> type-aware value engine
 -> local RAM

CAN read and CAN RX-write both converge on this parameter engine.

What is NOT yet proven:
parameter catalog slot
 -> exact CAN StdId family
 -> exact request/response command
 -> exact frame byte mapping
 -> exact setter-to-TX producer.

Therefore the full 260-row parameter<->CAN matrix is not yet CLOSED.

## 7. Strong structural model

For implementation:

ParameterRegistry
  |
  +-- ParameterDescriptor[260 catalog slots]
  |
  +-- runtime ParameterRecord[0x2C stride]
  |
  +-- TypeCodec
  |     +-- type1
  |     +-- type2
  |     +-- type3
  |     +-- type4
  |     +-- type5
  |
  +-- LocalValueStore
  |
  +-- CAN Read Scheduler
  |
  +-- CAN RX Write Decoder
  |
  +-- UI Binding

Do not collapse ParameterRegistry and CAN ID registry into one table.

## 8. Current status

CLOSED:
- parameter engine anchors;
- 260-slot catalog uniqueness;
- CAN read request construction;
- CAN RX parameter write path;
- UI local write path;
- common type engine.

OPEN:
- exact catalog-slot -> CAN ID graph for all 260;
- exact local-write -> CAN-TX bridge;
- exact 0x20008D84 ownership/layout;
- full getter/setter semantics per descriptor;
- complete response/publication mapping;
- exact instance mapping for multi-instance parameters.

## 9. Next attack

1. Resolve parameter record consumers after 0x08011812.
2. Resolve TX producers 0x08056A1C / 0x08056A44 and determine whether they are parameter-related.
3. Resolve [obj+0x14] initialization.
4. Build row-by-row catalog -> CAN matrix only after direct evidence exists.
