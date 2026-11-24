# TEKLAPELLET-CAN — ETAP 20 EXECUTION REPORT
Data: 2026-11-21
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## RAW EXPORT

### P1 — 0x0800FF50 final dispatch

Exact ending:

080100be: a902          add r1,sp,#0x8
080100c0: 6820          ldr r0,[r4]
080100c2: 6802          ldr r2,[r0]
080100c4: 6812          ldr r2,[r2]
080100c6: 4790          blx r2
080100c8: b008          add sp,#0x20
080100ca: e8bd 81f0     pop.w {r4,r5,r6,r7,r8,pc}

Therefore:
r0 = *(uint32_t *)0x200114C0
r2 = *(uint32_t *)r0
r2 = *(uint32_t *)r2
BLX r2

[NEW-HARD] The invoked method is vtable slot +0x00 of the object stored in field +0 of global object 0x200114C0.

Whole-BIN scan for C0 14 01 20 found exactly one occurrence: 0x08063D04. It is the literal used by 0x08063C3C before BL 0x0800FF50.

[OPEN] The constructor/runtime path that establishes [0x200114C0+0] was not recovered by the direct-address scan. This does not mean the field is uninitialized; its initialization is indirect or occurs through startup/data/object machinery.

Related but distinct object 0x200114CC is referenced at 0x080019D0, 0x0800D7A0 and 0x08063CF8. It must not be conflated with 0x200114C0.

### P2 — FUN_08011812

Current [sp+0x20] is original param_5 and current [sp+0x24] is original param_6.

With param_5 != 0:
record = base + index*0x2C
b = record[0x2C]
b must be 0x01 or 0x03, otherwise status 0x09.

[NEW-HARD] param_5=1 is an additional record-state/control gate. There is no dirty-bit store here.

With param_6 == 1, FUN_08011812 performs additional min/max/range validation using record fields around +0x1C and +0x14 and helper 0x08014734. With param_6 != 1 that extra branch is skipped.

[NEW-HARD] FUN_08011812 itself does not set a dirty bit, call 0x0806E59C, call 0x08057224, or invoke a post-write CAN callback. It validates and writes through record+0x0C according to the established type at record+0x10.

FUN_08037212 supplies param_5=1 and param_6=1. These arguments therefore mean additional record-state gating plus range validation, not a proven dirty notification.

### P3 — 0x080629FC

Whole-BIN Thumb scan found no direct BL/B.W to 0x080629FC and no direct call to 0x080629FD.

Common vtable:
physical table 0x08094508
slot 8 address 0x08094568
literal 0x080729FD
physical target 0x080629FC

0x080702F6 is inside constructor 0x080702DC and calls 0x080157A0 with r0 = r4 + 0x30. Constructor 0x080157A0 installs vtable 0x08094508.

The surrounding generic array constructor 0x0800DCD4 invokes 0x080702DC four times with base 0x200208EC, stride 0xD8 and count 4.

Enclosing instances:
0x200208EC, 0x200209C4, 0x20020A9C, 0x20020B74

Poller-bearing +0x30 subobjects:
0x2002091C, 0x200209F4, 0x20020AD0, 0x20020BA4

[NEW-STRONG] Four poller-containing subobjects are therefore instantiated through 0x080702DC.
[OPEN] The semantic identity of the enclosing 0x080702DC class is not proven to be a CAN manager.

## XREF / CALLGRAPH

Response TX:
CAN2 RX -> ReceivedCanMessages -> CanRxTask -> FUN_08063B80 -> 0x0800FF50 (object 0x200114C0) -> parse 0x600 frame -> FUN_08011812 -> build 0x580 response -> [obj] -> [vptr] -> slot 0 -> BLX.

Local parameter write:
FUN_08037212 -> FUN_08011812(..., param_5=1, param_6=1) -> state gate -> range validation -> write through record+0x0C -> status.

Poller:
0x080157A0 -> vtable 0x08094508 -> slot 8 -> 0x080629FC.
0x080702DC -> +0x30 subobject via 0x080157A0.
0x0800DCD4 -> four 0x080702DC instances.

## INTERPRETACJA

[NEW-HARD] 0x080100C6 invokes vtable slot 0, not an unknown slot.
[NEW-HARD] 0x200114C0 has exactly one direct literal reference in the BIN, at 0x08063D04.
[OPEN] [0x200114C0] and the constructor establishing it remain unresolved.
[REJECTED] 0x200114CC == 0x200114C0 is not supported.
[NEW-HARD] param_5=1 is a record-state gate, not a dirty setter.
[NEW-HARD] param_6=1 enables extra range validation.
[REJECTED] Dirty-bit/callback behavior inside FUN_08011812.
[NEW-HARD] No direct call to 0x080629FC exists outside vtable dispatch.
[NEW-STRONG] Four poller-containing subobjects are constructed through 0x080702DC.
[OPEN] CAN-specific semantic naming of the outer 0x080702DC class.

## STATUS

| Item | Status | Result |
|---|---|---|
| 0x080100BE..0x080100C6 dispatch offset | [NEW-HARD] | vtable slot +0x00 |
| 0x200114C0 direct literal references | [NEW-HARD] | exactly 1 |
| [0x200114C0] initialized pointer | [OPEN] | not recovered |
| 0x200114CC same as 0x200114C0 | [REJECTED] | distinct objects |
| param_5=1 | [NEW-HARD] | record-state gate |
| param_6=1 | [NEW-HARD] | range validation |
| dirty bit in 0x08011812 | [REJECTED] | absent |
| direct 0x080629FC callers | [NEW-HARD] | none |
| vtable slot 8 | [CONFIRMED-REPEAT] | 0x080629FC |
| 0x080702F6 | [NEW-STRONG] | constructs poller-bearing subobject |
| exact outer class role | [OPEN] | not proven |
| 0x20005EF0..0x20005F5B | [OPEN] | untouched |

## NEXT HIGHEST-VALUE TARGET

1. Resolve 0x200114C0 -> object -> vptr -> slot 0 -> actual TX function -> queue/CAN2.
2. Search outside FUN_08011812 for consumers of updated parameter storage and the UI-write-to-CAN bridge.
3. Keep 0x20005EF0..0x20005F5B as an independent open branch; no bytes are guessed.