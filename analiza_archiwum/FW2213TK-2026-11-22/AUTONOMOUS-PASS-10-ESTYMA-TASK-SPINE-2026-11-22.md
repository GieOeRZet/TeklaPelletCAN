# AUTONOMOUS PASS 10 — ESTYMA TASK SPINE / PARAMETER PUBLICATION BOUNDARY

Data: 2026-11-22

## Scope

Target: close the remaining scheduler path around `FUN_08010FCE`, identify the actual EstymaTask entry, and re-check whether the task itself reaches the parameter READ/TX path.

## HARD findings

### 1. EstymaTask entry is recovered

Task creation in `FUN_08062D82` uses:

- `FUN_08057630(DAT_08062EB0, s_EstymaTask_08062EC4, 0x3B6, 0, 3, 0, 0, 0)`

The task pointer was previously recovered directly from the firmware as:

- `DAT_08062EB0 -> 0x08062C95` (Thumb)
- physical function entry: `0x08062C94`
- name: EstymaTask

This is stronger than the earlier "task/dispatch likely indirect" statement: the actual task entry is now known.

### 2. EstymaTask does NOT directly call the parameter READ poller

Raw execution report for `0x08062C94` shows its direct-call set contains:

- `0x08063096`
- `0x0806316E`
- `0x08057952`
- `0x080630D4`
- `0x08062F18`
- `0x080577C2`
- `0x0800D92C`
- `0x080631A8`
- `0x080631AA`
- `0x08003921C`
- `0x080060518`

There is no direct call to:

- `0x080629FC` parameter READ poller
- `0x0806E59C` specialized CAN TX adapter
- `0x08010FCE` parameter sync/publication scheduler

Therefore the missing route to `FUN_08010FCE` is not a simple direct call from the main EstymaTask body.

### 3. The previously suspected local area is rejected again

The `0x08062900..0x080629FB` region contains the mathematical helper at `0x08062920`, then ends at the already-known poller `0x080629FC`.

No parameter WRITE/TX builder was recovered there.

Status: **REJECTED** as the missing publication path.

### 4. Scheduler boundary is narrowed

We now have:

`FreeRTOS task creation -> EstymaTask @ 0x08062C94`

but:

`EstymaTask main body -X-> FUN_08010FCE`

and:

`FUN_08010FCE` has no direct C caller in the decompiled blob.

The remaining scheduler mechanism is therefore constrained to one of:

1. an indirect callback/function-pointer invocation from EstymaTask or one of its helper routines,
2. a timer/periodic framework reached from the task,
3. another task/context not exposed as a direct C call in the decompilation.

No target is guessed.

## Additional hard re-check: publication sink

`FUN_08010FCE` and `FUN_0801117C` both call:

`[*(uint32_t **)(param_1 + 0x7180)] -> vtable slot 0`

with an 8-byte logical CAN message record.

Both paths construct:

- StdId = `0x0584`
- DLC = `8`
- command = `0x42`
- PID = tracked/round-robin record PID
- value = encoded from runtime type

The concrete +0x7180 object remains OPEN. The full decompilation blob contains only call sites for +0x7180 and no direct assignment to that field.

## Additional hard re-check: provider interface

+0x7178 remains a bidirectional provider object:

- vtable slot 0: GET(PID, 5-byte typed descriptor) -> status
- vtable slot +4: SET(PID, value, runtime type) -> status

It is used both during registration and periodic synchronization.

No direct assignment to +0x7178 exists in the decompiled blob.

## Current closure status

CLOSED:
- EstymaTask task entry
- task creation path
- rejection of direct EstymaTask -> parameter READ poller
- rejection of 0x08062920 region as missing TX builder
- +0x7180 call contract
- +0x7178 call contract

OPEN:
- exact scheduler/callback route to `FUN_08010FCE`
- concrete +0x7178 implementation
- concrete +0x7180 implementation
- sidecar 1/2/3 exact semantics
- second comparison source in `FUN_0801100C`

## Evidence discipline

No new inference is promoted to HARD merely because an address is plausible. The task pointer is HARD because it was recovered from the firmware execution/static analysis report; the negative direct-call result is HARD from the recovered EstymaTask disassembly.

