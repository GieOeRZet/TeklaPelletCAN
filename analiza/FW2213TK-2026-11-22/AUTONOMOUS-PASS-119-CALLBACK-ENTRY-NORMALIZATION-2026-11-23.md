# AUTONOMOUS PASS 119 — CALLBACK ENTRY-POINT NORMALIZATION — 2026-11-23

## New hard fact

Descriptor word0 values are Thumb entry pointers, not necessarily function starts.

- descriptor 0x38790 -> 0x08048493
- Ghidra function table: function start 0x08048468, size 0x48
- therefore 0x08048493 is an interior entry point at offset +0x2B inside FUN_08048468.

For selector 18:

- descriptor 0x387B8 -> 0x080485A1
- Ghidra function table: function start 0x0804858A, size 0x9A
- therefore 0x080485A1 is an interior entry point at offset +0x17 inside FUN_0804858A.

## Consequence

Previous wording 'callback function 0x08048493 / 0x080485A1' is normalized to **callback entry point**. Naming them as independent top-level functions would be wrong.

This is important because the two selectors may enter different basic blocks of larger shared routines. Semantic analysis must start at the exact entry address, not the Ghidra function start.

## Existing evidence

FUN_08048468 body contains host/content operations and calls:
- FUN_0802e652
- FUN_08034d74
- FUN_0802eade
- FUN_08032316

But this body-level evidence does NOT prove that the interior entry 0x08048493 executes the same sequence. The exact basic block at +0x2B remains OPEN.

For FUN_0804858A the committed repository currently provides the function boundary but no decompiled body, so 0x080485A1 remains OPEN at instruction level.

## Next

Recover exact instruction/basic-block bodies at 0x08048493 and 0x080485A1, then trace their outgoing calls. Do not inherit semantics from containing function starts without CFG proof.
