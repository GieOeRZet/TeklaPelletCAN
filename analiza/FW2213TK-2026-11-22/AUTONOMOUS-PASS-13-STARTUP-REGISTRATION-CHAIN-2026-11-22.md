# AUTONOMOUS PASS 13 — STARTUP REGISTRATION CHAIN

Date: 2026-11-22

## HARD

Recovered call chain:

FUN_08062D82 (system startup/task creation)
 -> FUN_08000E34()
 -> FUN_08001AE4()
 -> FUN_0801143C() x3

FUN_08001AE4 is therefore a startup registration routine, not an EstymaTask periodic routine.

FUN_08001AE4 registers exactly:
- 0x3500 / Main module type / sidecar 3
- 0x3502 / CH expansion module type / sidecar 3
- 0x350B / Profile number / sidecar 3

FUN_08000E34 is called directly by FUN_08062D82 before the four FreeRTOS tasks are created.

Therefore the three visible static registrations are established during system initialization, before task execution.

## Important boundary

This gives a clean separation:

STARTUP:
task/bootstrap -> FUN_08000E34 -> FUN_08001AE4 -> parameter registration

RUNTIME:
unknown indirect framework -> FUN_08010FCE -> provider sync/publication

The recovered C export contains no direct edge between these two chains.

## OPEN

The missing bridge is now specifically the runtime object/framework that owns the parameter table and its +0x7178/+0x7180 interfaces.

No claim is made that EstymaTask itself owns that object.