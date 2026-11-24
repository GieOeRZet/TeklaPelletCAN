# AUTONOMOUS PASS 14 — RUNTIME CALLBACK OBJECT / PARAMETER MANAGER BRIDGE — 2026-11-22

Firmware SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Size: 2031616 bytes

## Hard closure

### Unique vtable for FUN_08010FCE

Physical vtable/data region 0x080A44F0 contains a unique pointer:
- slot 0 -> 0x08010FCE
- slot 1 -> 0x0805926C
- slot 2 -> 0x0805967C
- slot 7 -> 0x0806E59C
- slot 10 -> 0x080629FC
- slot 11 -> 0x08063798
- slot 14 -> 0x08063FD0
- slot 15 -> 0x0800FEA4
- slot 16 -> 0x0800DBD2
- slot 18 -> 0x0800EE60

The pointer 0x080A44F0 is installed by constructor-like routine 0x0800DDE4.

### Startup construction

FUN_08000E34 directly calls 0x0800DDE4 seven times:
- 0x08000266 with ID 0x78
- 0x0800027A with ID 0x7A
- 0x0800028E with ID 0x7B
- 0x080002A2 with ID 0x7C
- 0x080002B6 with ID 0x7D
- 0x080002CA with ID 0x7E
- 0x080002DE with ID 0x7F

Six objects are placed relative to startup main object 0x20008CD0:
- +0x7238 = 0x2000FF08
- +0x72B0 = 0x2000FF80
- +0x7328 = 0x2000FFF8
- +0x73A0 = 0x20010070
- +0x7418 = 0x200100E8
- +0x7490 = 0x20010160

Constructor 0x0800DDE4 writes vptr=0x080A44F0 and the ID/instance fields.

### Runtime-installed callback group

FUN_08000E34 also constructs a concrete structure at:
0x200208EC + 0x174C = 0x20022038.

It installs pointers to the callback objects:
- [0x20022038+0x34] = main+0x7238
- [0x20022038+0x38] = main+0x72B0
- [0x20022038+0x3C] = main+0x7328
- [0x20022038+0x40] = main+0x7490

These are exact MOVW/ADD/STR sequences in FUN_08000E34.

Therefore the startup path now has a concrete runtime object group whose members are objects with vtable slot 0 = FUN_08010FCE.

### Scheduler body and provider/publication interfaces

FUN_08010FCE:
- calls FUN_08011368(this)
- calls FUN_0801117C(this)
- performs periodic parameter processing.

FUN_08011368 uses main+0x7178:
- loads object from [this+0x7178]
- calls vtable slot 0 for GET
- on mismatch/write-back calls vtable slot +4.

FUN_0801117C uses main+0x7180:
- loads object from [this+0x7180]
- calls vtable slot 0 with the prepared 8-byte logical CAN publication record.

FUN_0801143C also uses +0x7178 during registration.

## Current boundary

The runtime callback/object bridge to FUN_08010FCE is now materially resolved from the canonical BIN.

Still requiring independent concrete-object evidence:
- exact object/vtable behind +0x7178;
- exact object/vtable behind +0x7180;
- complete indirect scheduler invocation proof from runtime, rather than only the startup-installed object graph.

Do not promote those three points to HARD without new raw/runtime evidence.
