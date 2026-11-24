# NewEstyma — PARAMETER SYNC / PUBLICATION INTERFACE CLOSURE 06 — 2026-11-22

Source: complete Ghidra decompilation blob 9620d0c85259d34bb6a20d3b03b038945dfe4c1a.

## 1. object+0x7178 is a parameter-provider interface

All recovered uses are indirect virtual calls through the object stored at `param_1+0x7178`.

Call shape A (getter):
`interface(PID, destination_5byte_descriptor)` -> status.

Call shape B (setter):
vtable slot `+4` with `(PID, value, type)`.

This is hard evidence from FUN_08011368 and FUN_0801143C. The interface is therefore a generic parameter synchronization/provider service, not a CAN transport primitive itself.

The exact concrete vtable/type behind `+0x7178` remains OPEN because the decompilation blob contains no direct assignment to this offset.

## 2. Registration-time synchronization is closed

FUN_0801143C registers a record, stores its class/state byte, then:

- always performs initial value validation/update through FUN_08011812;
- if class/state is 2 or 3, calls the +0x7178 provider getter for that PID;
- converts the returned value to the parameter's runtime type;
- writes the provider value back through FUN_08011812.

For signed-16 parameters it explicitly preserves type 4; otherwise the synchronized value is treated as type 3 (u32) before the write.

So classes 2/3 are not merely labels: they trigger provider synchronization during registration.

## 3. Periodic synchronization is closed at the algorithm level

FUN_08011368 performs the same provider synchronization later:

- scans records using the canonical 0x2C stride;
- selects only side-car/state 2 or 3;
- provider getter: `(PID, buffer)`;
- compares provider value against the current local value using the resolved runtime type;
- on mismatch or provider error, calls provider vtable slot +4 to update the provider/local synchronization state.

The provider's concrete implementation remains OPEN, but the caller-side synchronization algorithm is now closed.

## 4. Publication path is a distinct interface at +0x7180

FUN_0801117C emits a parameter-change CAN publication through the indirect function at `object+0x7180`.

Hard frame fields constructed by the caller:

- Standard CAN ID: `0x0584`
- DLC: `8`
- command/data byte: `0x42`
- parameter PID: 16-bit value
- value: encoded according to runtime parameter type

The function is called only after a tracked parameter value changes. Therefore `+0x7180` is a message/frame publication sink, distinct from the parameter-provider interface at `+0x7178`.

The exact concrete implementation behind +0x7180 remains OPEN; its caller-side contract is closed.

## 5. New model boundary

Parameter engine now has three distinct layers:

1. record engine: PID/storage/type/min/max/default;
2. provider synchronization: object+0x7178 getter/setter;
3. CAN publication: object+0x7180 sink producing 0x0584/0x42 notifications.

Do not collapse layers 2 and 3 into one CAN setter without new evidence.

## Remaining targets

- recover concrete object/vtable for +0x7178;
- recover concrete object/function for +0x7180;
- enumerate all PIDs selected by FUN_0801117C;
- map provider classes 1/2/3 to concrete registrations;
- recover meaning of `R+0x30` / `param_9` and remaining registration arguments.
