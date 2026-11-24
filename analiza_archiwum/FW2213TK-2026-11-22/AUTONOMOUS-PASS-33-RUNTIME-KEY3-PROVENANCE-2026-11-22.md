# AUTONOMOUS PASS 33 — RUNTIME KEY 3 / PARAMETER RECORD PROVENANCE — 2026-11-22

## Objective
Follow class-12 key 3 past 0x080115F6 and determine what kind of identifier it is, how the runtime record is found, and whether it can be directly equated with a catalog PID.

## HARD findings

### 1. 0x080115F6 is a runtime-record lookup, not the PID resolver
At PROJECT 0x080115F6 the function receives:
- r0 = output temporary,
- r1 = parameter-manager object,
- r2 = lookup key.

It scans the manager runtime table starting at manager+0x08.
Each record has stride 0x2C.

The search examines three records per 0xB0 block:
- current record ID at +0x00,
- next record ID at +0x2C,
- next record ID at +0x58,
then advances the scan pointer by 0xB0.
The scan bound is 0x294 (660 runtime positions).

When a match is found:
- record address = manager + 0x08 + index*0x2C;
- +0x0C is dereferenced as the value-storage pointer;
- +0x10 supplies the runtime type byte;
- the resulting value/type pair is returned through the temporary object.

Therefore class-12 key 3 is a lookup key into the runtime parameter table.

### 2. Key 3 is initialized as a real runtime parameter record
Startup code around PROJECT 0x08001D62 calls 0x0801143C with:
- manager = 0x20008D84,
- key = 3,
- storage pointer = 0x20021FAA,
- type code = 1.

The storage pointer is derived exactly as:
0x200208EC + 0x16BE = 0x20021FAA.

The type code 1 comes from the type byte of the local descriptor passed through 0x08010FC2.

### 3. The manager runtime table is populated through 0x0801143C
0x0801143C searches the same 660-slot runtime table, allocates/reuses the matching slot, and stores:
- record +0x08 = lookup key,
- record +0x0C = storage pointer,
- record descriptor/type metadata through the typed-value helper.

Thus key 3 is not merely a UI-local temporary variable. It is a concrete runtime parameter-record identifier.

### 4. Catalog PID equivalence is NOT proven
The class-12 path uses key 3.
The runtime-record table stores that key.
However, no direct evidence in this pass equates key 3 with one of the 260 catalog PIDs.

Therefore the earlier wording "logical key 3" is retained only as a convenient label; the stronger and safer machine-level term is:
**runtime parameter lookup key 3**.

## Class-12 chain after this pass

class12
 -> 0x080373BA
 -> 0x080115F6(manager=0x20008D84, key=3)
 -> runtime record for key 3
 -> value/type read
 -> +1
 -> 0x08011812(manager, key=3, type=5)
 -> caller +1
 -> modulo 8
 -> 0x08011812(manager, key=3, type=5)
 -> return 0..7

## New OPENs

1. Exact semantic/PID identity represented by runtime key 3.
2. Why startup stores key 3 at storage 0x20021FAA.
3. Exact field identity around 0x20021FAA relative to the configuration object at 0x200208EC.
4. Whether class 12's two writes intentionally target the same record despite the type changing from the startup descriptor's type 1 to write type 5.
5. Complete caller/UI meaning of the 0..7 result.

## Rejected/corrected

- REJECTED: treating 0x080115F6 itself as the catalog-PID resolver.
- REVISED: "logical key 3" -> "runtime parameter lookup key 3" unless a direct PID mapping is later proven.

## Next attack

1. Recover all startup records around key 3/4 and map their storage offsets/types.
2. Trace reads/writes of 0x20021FAA and neighboring fields.
3. Search for direct key-3 -> catalog/PID bridges.
4. Continue provider vtable slots, but only promote slots whose targets are proven executable/interface methods.
