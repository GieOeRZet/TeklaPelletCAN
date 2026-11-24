# PARAMETER RESPONSE DISPATCH — 100% CLOSURE
Date: 2026-11-22

## Scope
Exact final dispatch of the parameter-message receiver at 0x0800FF50.

## Hard closure
The handler at 0x0800FF50 receives a frame with StdId = object+0x08+0x600, decodes parameter index/type/value, invokes FUN_08011812, constructs the response-like frame with StdId = object+0x08+0x580 and command 0x80, then dispatches it at:

0x080100BE:
  add r1,sp,#8
0x080100C0:
  ldr r0,[r4]
0x080100C2:
  ldr r2,[r0]
0x080100C4:
  ldr r2,[r2]
0x080100C6:
  blx r2

Therefore:
- r0 = object field +0
- r2 = object field +0 -> first word
- r2 = second word of that object
- BLX executes the object's vtable slot +0x00.

The global object passed by the dispatcher is 0x200114C0.
Whole-BIN scan found exactly one literal reference to 0x200114C0, at 0x08063D04, loaded by 0x08063C3C before BL 0x0800FF50.

## CLOSED
- final dispatch mechanism: 100%
- dispatched slot: vtable +0x00
- owning global context: 0x200114C0
- response frame construction: 100% at handler level
- local parameter update call: FUN_08011812

## OPEN and deliberately excluded
- concrete constructor/initializer of [0x200114C0+0]
- concrete implementation behind the slot +0x00 object
- semantic naming of the +0x600/+0x580 protocol as CANopen SDO

No inference was promoted to HARD beyond the exact machine-level dispatch.
