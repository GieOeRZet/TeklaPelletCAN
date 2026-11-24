# AUTONOMOUS PASS 134 — 0x08062674 SUB-ENTRY CORRECTION — 2026-11-23

## Correction
PASS 133 treated 0x08062674 as an independent 18-byte function. That is incorrect.

Canonical functions.txt defines:
- FUN_08062638 at 0x08062638, size 718 bytes.

Therefore 0x08062674 lies inside FUN_08062638 at offset +0x3C.

Raw bytes at 0x08062674 begin with:
- 0x08062674: 4770 = BX LR
- following bytes continue with 6001, 7102, 6083, 9900, 60C1, 9901, 6101, 4770.

Thus the provider slot-4 call to 0x08062674 is a call to an **interior immediate-return sub-entry** inside FUN_08062638, not a standalone function.

## Correct slot-4 behavior
The 38-byte routine at 0x080617FE:
1. writes 0x200248A4 to object +0x00;
2. performs the indirect BLX through the value loaded via 0x200248A8;
3. calls real function FUN_08061E78 with object +0x24;
4. calls interior sub-entry 0x08062674 (+0x3C inside FUN_08062638), which immediately returns;
5. returns the original object pointer.

FUN_08061E78 is independently a 10-byte function that clears offsets +0x08 and +0x0C of its argument.

## Literal-pool clarification
Occurrences of 0x200248A4/0x200248A8 at RAW 0x52650/0x52658 are inside the literal pool of FUN_08062638 and do not by themselves prove another direct call site. The slot-4 function has its own literal pool at RAW 0x51A38/0x51A3C.

## Semantic boundary
Slot 4 remains strongly initialization/reset-like at machine level because it installs an object pointer/table value and clears object state through a helper, but the exact class/object identity and meaning of 0x200248A4/0x200248A8 remain OPEN.

PASS 134 supersedes the specific claim in PASS 133 that 0x08062674 is an independent 18-byte function.