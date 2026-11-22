# NewEstyma — CURRENT PROJECT STATE

Date: 2026-11-22

## Goal
Full universal reconstruction of Estyma firmware behavior, eventually targeting ESP32-C6 + CAN and reusable cross-platform model.

## HARD highlights
- CAN2 RX/TX transport and hardware path.
- Node 4 object architecture.
- Parameter resolver and typed storage model.
- 260-entry catalog uniqueness.
- 660-record runtime search space, stride 0x2C.
- PID/storage/type geometry.
- +0x14 MIN, +0x1C MAX, +0x24 DEFAULT descriptors.
- Basic parameter READ/WRITE protocol paths.
- MenuTree control-flow mechanism.
- Concrete parameter manager 0x20008D84.
- Concrete provider 0x20008D64 behind +0x7178.
- Concrete publication sink 0x20008D60 behind +0x7180.
- Scheduler registration leading to FUN_08010FCE.

## Main OPENs
- Complete provider vtable 0x080A31F0 interface; slot targets currently OPEN.
- Full 260-row cross-layer matrix.
- Descriptor/record ownership and multi-instance mapping.
- Local parameter write -> outbound CAN publication bridge.
- Complete UI semantic graph and visibility mapping.
- Sidecar class 1/2/3 exact semantics.
- Complete response/publication graph.

## Current parameter-manager architecture
Constructor: 0x0800DDC0
this = 0x20008D84
provider = 0x20008D64
sink = 0x20008D60
manager vtable = 0x080A44F0
manager vtable slot 0 = FUN_08010FCE
provider vtable = 0x080A31F0

## Protocol anchors
READ: StdId 0x0604, command 0x40
Publication: StdId 0x0584, command 0x42

Do not confuse:
- catalog 260 with runtime 660
- RAW offset with PROJECT address
- manager/provider/sink objects
- MenuTree selector with runtime class byte
- mechanism closure with semantic closure
