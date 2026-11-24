# AUTONOMOUS PASS 126 — PROVIDER SLOT 4 EXACT TARGET — 2026-11-23

## Objective
Re-open the provider vtable at the canonical raw address and resolve slot 4 without relying on older semantic labels.

## HARD evidence

Provider vtable:
- runtime vptr: `0x080A31F0`
- PROJECT: `0x080931F0`
- RAW: `0x931F0`

Canonical raw bytes at RAW `0x931F0` begin:
```
31 db 01 08
79 db 01 08
00 00 00 00
00 00 00 00
ff 17 06 08
```

Therefore the first five vtable entries are:
- slot 0: runtime `0x0801DB31`
- slot 1 (+0x04): runtime `0x0801DB79`
- slot 2 (+0x08): `0x00000000`
- slot 3 (+0x0C): `0x00000000`
- slot 4 (+0x10): runtime `0x080617FF`

The target `0x080617FF` is Thumb and normalizes to physical function-address space as an **interior entry**:
- containing recovered function: `FUN_080617DC`
- function start: `0x080617DC`
- target offset: `+0x23`
- containing function size: 124 bytes

`FUN_080617DC` is independently identified as the CAN2 RX mailbox serializer: it reads RIR/RDTR/RDLR/RDHR from CAN2 FIFO0 and constructs the 20-byte RX record. The repository has independent evidence for its use from the CAN2 RX ISR path `0x0806F9F8 -> FUN_080617DC -> ReceivedCanMessages`.

## Correction

The previous wording that provider slot 4 was an "additional provider/object state/init transition" is **not sufficiently supported and is superseded**.

What is now HARD is only:
```
provider vtable slot +0x10
    -> runtime pointer 0x080617FF
    -> interior entry +0x23 of FUN_080617DC
```

Do **not** rename slot 4 as a provider state/init method.

## Important boundary

The exact basic block entered at `FUN_080617DC+0x23` is not available from the committed text decompilation because `firmware/FW2213TK-ghidra/decompiled.c` is stored as an empty Git blob with SHA `9620d0c85259d34bb6a20d3b03b038945dfe4c1a`. The function list proves the containing function and size, but not the exact +0x23 CFG block.

Therefore the semantic meaning of provider slot 4 remains OPEN pending raw instruction/CFG evidence. No semantics are fabricated.

## Consequence for model

The provider interface is currently:
- slot 0: GET contract CLOSED
- slot +0x04: SET contract CLOSED
- slot +0x08: NULL
- slot +0x0C: NULL
- slot +0x10: **interior CAN RX serializer target; exact callback-entry semantics OPEN**

This is a materially stronger and more accurate result than the former "state/init transition" label.

## Next target

1. Recover raw bytes/instruction boundary for `0x080617FF` and CFG from firmware/Ghidra export.
2. Then continue the 260-slot registration/catalog matrix.
3. In parallel continue UI classes 11/13/15/18/19/20 and sidecar 1/2/3.
