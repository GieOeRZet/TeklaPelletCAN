# AUTONOMOUS PASS — MENU SELECTOR 8/9 CLOSURE + D60 SOURCE RECONCILIATION
Date: 2026-11-22

## 1. HARD CLOSURE — selector 8/9 capability gates

The repository's reverse-engineering evidence consistently gives:

- selector 8 -> internal index 0x11C -> CAN PID 0x350C -> visible iff value != 0
- selector 9 -> internal index 0x122 -> CAN PID 0x3525 -> visible iff value != 0

This is the capability/visibility resolver layer, not navigation.

Therefore the following edge is closed at the resolver level:

selector 8 -> 0x11C -> 0x350C -> nonzero gate
selector 9 -> 0x122 -> 0x3525 -> nonzero gate

This does NOT claim that 0x350C/0x3525 alone define the complete destination screen behavior; that remains a separate navigation/resource problem.

## 2. D60 / vptr reconciliation

Earlier/current documentation contains a conflict.

One current master statement says:
[0x20008D60] = 0x080A4544 -> PROJECT vtable 0x08094544 -> slot 0 0x0806E59D/FUN_0806E59C.

However the canonical-BIN-derived OPEN1 evidence explicitly reports:
- whole-BIN direct LE32 occurrences of 0x20008D60: 0
- whole-BIN direct LE32 occurrences of 0x080A4544: 0
- 0x080A4568 occurs once, for the separate object 0x2002466C
- startup/decompression path 0x08094644 -> 0x0808F74C -> 0x08062D82 is NOT a conventional .data/.bss copy into 0x20008D60.

Therefore the statement that startup/decompression itself "confirms" the D60 vptr is too strong unless an actual runtime write/constructor path is recovered.

Status after this pass:
D60 vptr -> 0x080A4544: OPEN, not promoted to HARD.
D60 slot 0 -> FUN_0806E59C: OPEN pending direct runtime/object-construction proof.

## 3. Rule

RAW BIN remains the source of truth. Repository summaries may be corrected when they overstate evidence.
