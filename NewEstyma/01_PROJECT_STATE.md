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
- Provider vtable 0x080A31F0: slots 0/1 HARD (GET/SET); remaining interface OPEN.
- Full 260-row cross-layer matrix.
- Descriptor/record ownership and multi-instance mapping.
- Local parameter write -> outbound CAN publication bridge (machine-level HARD; timing/shadow semantics OPEN).
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
provider vtable runtime = 0x080A31F0
provider vtable PROJECT = 0x080931F0
provider vtable RAW = 0x931F0
provider slot0 GET = runtime 0x0801DB31 / PROJECT 0x0800DB31
provider slot1 SET = runtime 0x0801DB79 / PROJECT 0x0800DB79

## Protocol anchors
READ: StdId 0x0604, command 0x40
Publication: StdId 0x0584, command 0x42

Address rule:
- runtime pointer = PROJECT + 0x10000
- PROJECT = RAW + 0x08000000
- never index RAW using a runtime pointer directly.

Do not confuse:
- catalog 260 with runtime 660
- RAW offset with PROJECT address
- manager/provider/sink objects
- MenuTree selector with runtime class byte
- mechanism closure with semantic closure


## PASS 20 closure

`FUN_08011812` writes the validated local value into record storage; `FUN_0801117C` detects local/shadow changes and builds StdId 0x0584 command 0x42; +0x7180 resolves to 0x20008D60; sink slot0 resolves to FUN_0806E59C; TX queue/CAN2 path is already HARD. The machine-level local-write -> outbound publication bridge is CLOSED.


## PASS 21 — MenuTree raw/runtime anchor audit

Canonical BIN re-scan is now automated by `tools/menu_matrix_scan.py`.

HARD:
- 21×6 B MenuTree table at RAW 0x42348 / PROJECT 0x08042348.
- Runtime class table pointer 0x20005EF0 has one direct literal anchor at RAW 0x3C218.
- Access/update table pointer 0x20005F08 has one direct literal anchor at RAW 0x42314.
- Row constructor Thumb pointer 0x0805BB43 has one literal anchor at RAW 0x3C030.
- Main row-selection resolver 0x0808EB01 has one literal anchor at RAW 0x63AB8.
- Sibling resolver 0x0808EB37 has one literal anchor at RAW 0x63AC0.
- Root-table selector is not itself the direct page-navigation key; runtime class dispatch remains a separate layer.

OPEN:
- producers and runtime contents of 0x20005EF0 and 0x20005F08;
- exact runtime class -> screen/widget mapping;
- complete widget tree, visibility/access matrix and PID/CAN cross-link.
