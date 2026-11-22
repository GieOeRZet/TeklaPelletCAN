# AUTONOMOUS PASS 32 — CLASS 12 PARAMETER-3 CYCLIC OPERATION — 2026-11-22

## Objective
Close the previously OPEN semantic branch for runtime class 12 and verify the exact parameter-manager operation, including the concrete manager object.

## Canonical source
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Address mapping:
- RAW -> PROJECT = +0x08000000
- runtime -> PROJECT = -0x10000

## HARD findings

### 1. Class 12 entry is an exact special path
At RAW 0x3C12A / PROJECT 0x0803C12A:
- load object +0x08
- call PROJECT 0x080373BA
- increment returned value
- load object +0x08 again
- call PROJECT 0x080373E6
- branch to RAW 0x3C250.

This is the exact class-12 branch of the 21-byte runtime-class TBB dispatcher.

### 2. 0x080373BA operates on logical parameter key 3
PROJECT 0x080373BA:
- builds temporary typed value;
- passes literal 3 as the logical key to PROJECT 0x080115F6;
- the literal at RAW 0x3754C is exactly 0x20008D84, the known concrete parameter-manager object;
- the fetched value is returned as the manager-resolved type-5 value;
- the function increments it;
- it writes the incremented value back through PROJECT 0x08011812 using logical key 3 and type 5;
- returns the incremented value.

### 3. 0x080373E6 performs modulo-8 writeback for the same logical key
PROJECT 0x080373E6:
- computes r1 % 8;
- constructs a type-5 value;
- calls PROJECT 0x08011812;
- uses logical key 3;
- uses manager object 0x20008D84;
- returns the modulo-8 result.

### 4. Combined class-12 behavior
The exact sequence is therefore:

class12 input
 -> GET logical key 3
 -> value := value + 1
 -> SET logical key 3, type 5
 -> caller increments returned value again
 -> value := value % 8
 -> SET logical key 3, type 5
 -> return modulo-8 value

The first increment is not merely local: 0x080373BA commits it through 0x08011812 before returning.

## Evidence
- RAW 0x3C12A..0x3C13A: class-12 dispatch path.
- RAW 0x373BA..0x37412: parameter-3 get/increment/set.
- RAW 0x373E6..0x37412: modulo-8 set/return.
- RAW 0x3754C: 0x20008D84.
- PROJECT 0x08011812: established parameter update/commit primitive.

## Interpretation boundary
HARD:
- logical key = 3;
- concrete manager = 0x20008D84;
- type = 5;
- two write operations;
- second operation is modulo 8;
- class 12 returns the modulo-8 result.

STRONG:
- class 12 is a cyclic selector/state operation over an 8-value domain.

OPEN:
- semantic UI label/visible widget controlled by parameter 3;
- exact mapping of logical key 3 to catalog/non-catalog PID;
- whether the intermediate first write is intentionally observable externally before the modulo-8 write;
- caller-level meaning of the returned 0..7 state.

## Negative / rejected
No new rejected hypothesis in this pass.

## Next attack
1. Resolve logical key 3 through the runtime resolver and determine its descriptor/PID/storage/type.
2. Trace all callers of the class-12 construction/action path.
3. In parallel continue provider remaining slots and persistence.
4. Continue UI graph from runtime class -> callback object -> concrete widget/resource/action.

