# NewEstyma — RECORD/DESCRIPTOR HARD CLOSURE 03 — 2026-11-22

## Executive finding

Direct inspection of the complete Ghidra decompilation blob closes the 0x2C record body.

The runtime parameter record is exactly 0x2C bytes. The three descriptor fields are not opaque 5-byte blobs anymore: each is a compact {u32 value, u8 type} descriptor.

### Record R(i)

R(i) = base + i*0x2C

| offset | size | HARD role |
|---:|---:|---|
| +0x00..+0x07 | 8 | prefix/adjacent-slot metadata area; not yet semantically closed |
| +0x08 | 2 | external parameter/CAN PID |
| +0x0A | 2 | currently not semantically closed |
| +0x0C | 4 | pointer to current local value storage |
| +0x10 | 1 | value type 1..5 |
| +0x11..+0x13 | 3 | padding/reserved/unknown |
| +0x14 | 5 | descriptor {u32 value, u8 type} |
| +0x19..+0x1B | 3 | padding/reserved/unknown |
| +0x1C | 5 | descriptor {u32 value, u8 type} |
| +0x21..+0x23 | 3 | padding/reserved/unknown |
| +0x24 | 5 | descriptor {u32 value, u8 type} |
| +0x29..+0x2B | 3 | padding/reserved/unknown |

Total = 0x2C = 44 bytes exactly.

## HARD proof — descriptor primitive

FUN_08014728 is a 5-byte copy helper. It is a wrapper around FUN_08015260 with length 5.

FUN_08014734 interprets a 5-byte descriptor:
- byte 0..3 = value
- byte 4 = type
- type 1 -> u8
- type 2 -> u16
- type 3 -> u32
- type 4 -> signed 16-bit
- type 5 -> signed/32-bit path

Therefore +0x14/+0x1C/+0x24 are exact typed value descriptors, not arbitrary metadata.

## HARD proof — registration

FUN_0801143C:
- R+0x08 = param_2
- R+0x0C = param_3
- R+0x14 = copy5(param_5)
- R+0x1C = copy5(param_7)
- R+0x24 = copy5(param_11)
- R+0x10 = param_4
- R+0x2C = (byte)param_10
- R+0x30 = param_9

It then decodes +0x24 through FUN_08014734 and may pass that value through FUN_08011812.

It also performs a special post-registration update for param_10 == 2 || param_10 == 3.

## IMPORTANT correction to the previous 0x2C rejection

The previous statement that record+0x2C is simply not a field was geometrically correct but semantically incomplete.

The direct code proves that FUN_0801143C deliberately writes:
R(i)+0x2C = param_10
R(i)+0x30 = param_9

Those addresses are physically the first 8 bytes of R(i+1) under the 0x2C stride.

Therefore the correct model is:
- +0x2C/+0x30 are NOT fields inside the 44-byte body of R(i);
- they ARE deliberately used by firmware as an adjacent-slot/prefix metadata area associated with the registration operation;
- FUN_08011812 with param_5 != 0 reads R(i)+0x2C and accepts only 1 or 3;
- thus the state/access gate used by that path is physically stored at the beginning of the next 0x2C slot.

Do NOT collapse this into record size 0x30: lookup/registration stride remains hard 0x2C.

## HARD — getter matrix

For a PID lookup:
- FUN_080115F6 returns value from **(R+0x0C) and type from R+0x10;
- FUN_0801167A returns descriptor at R+0x14;
- FUN_080116E6 returns descriptor at R+0x1C;
- FUN_0801155A returns descriptor at R+0x24;
- FUN_080117B4 writes/replaces the descriptor at R+0x24.

This gives the first complete getter/setter matrix for the descriptor layer.

## HARD — 0x11812 validation

FUN_08011812:
1. resolves PID using the same 0x2C-stride scan;
2. if param_5 != 0, reads R+0x2C and requires 1 or 3;
3. uses R+0x10 as the destination value type;
4. writes through *(R+0x0C);
5. if param_6 == 1, compares incoming value against descriptor +0x1C and compares descriptor +0x14 against incoming value;
6. returns explicit status codes.

Thus +0x14 and +0x1C are not merely metadata: they participate directly in range validation.

## HARD — initialization/reset role

FUN_0801113A:
- asks FUN_0801100C for a parameter whose value is outside the descriptor-defined range;
- obtains its +0x24 descriptor via FUN_0801155A;
- calls FUN_08011812(..., param_5=0, param_6=1).

This establishes +0x24 as the reset/repair/default-side value used by the range-repair path.

## Platform-agnostic model now

PID
 |
 v
R(i) @ base+i*0x2C
 |
 +-- +0x08 PID
 +-- +0x0C --> current value storage
 +-- +0x10 --> type
 +-- +0x14 --> typed descriptor used as one range boundary
 +-- +0x1C --> typed descriptor used as the other range boundary
 +-- +0x24 --> reset/default descriptor
 |
 +-- adjacent R(i+1)+0x00 --> state/access byte written by registration
 +-- adjacent R(i+1)+0x04 --> registration metadata/pointer

The exact semantic names lower/upper/default are role-level interpretations from validation/repair behavior; every individual parameter still needs caller mapping.

## Remaining OPEN
1. exact semantics of R+0x00..+0x07 and why registration stores R(i) sidecar data into R(i+1) prefix;
2. exact semantic role of R+0x0A;
3. exact signedness/64-bit behavior for type 5;
4. full mapping of registration arguments param_5/7/11 across all parameter families;
5. complete PID -> descriptor -> UI/CAN matrix.

## Source

Primary source: complete Ghidra decompilation blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a.
Cross-checked against the established 0x2C stride and runtime-engine findings.