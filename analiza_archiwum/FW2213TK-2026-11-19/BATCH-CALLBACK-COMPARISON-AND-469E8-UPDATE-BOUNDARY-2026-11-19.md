# BATCH — CALLBACK COMPARISON + 469E8 UPDATE BOUNDARY — 2026-11-19

## Result
Ten przebiegów doprowadziły do korekty dwóch granic architektury.

## 1. Parameter callback fields
3709→0x0801425C; 370A→0x0801AB7E; 370B→0x08015CCC; 370C→0x0801659E; 370D→0x08016614.
0x0801425C leży wewnątrz FUN_0801417C; 0x0801659E i 0x08016614 wewnątrz FUN_080164F4; 0x08015CCC nie jest początkiem nazwanej funkcji.
Therefore callback/code field is not necessarily a normal function entrypoint.
0x0801AB7E remains an unresolved internal/raw boundary between recognized regions. Do not name it as a function.

## 2. 469E8
FUN_080469E8 installs DAT_08046CC4, constructs Bitmap child +0x4F, writes resource ID 14 using FUN_080307BC, then registers itself through FUN_080318B4.
FUN_080318B4 is registry/reference counting. It is not the parameter update.
FUN_080317AE dispatches registered objects through vtable slot +0x50.

## 3. Architecture after correction
Branch A: 370A → RAM 0x20021FA6 → callback 0x0801AB7E → unknown dispatcher.
Branch B: active module → FUN_080318B4 → FUN_080317AE → DAT_08046CC4+0x50 → unknown 469E8 update → child +0x4F → Bitmap/resource.
Direct 370A→469E8 is NOT proven.

## 4. Next attack
Recover the shared parameter callback dispatch using 3709/370B/370C/370D as controls, then recover DAT_08046CC4+0x50, trace the update method, find the variable resource ID, and only then map 370A to assets 011..014.

## Evidence labels
[FW] direct decompiled/function-range evidence.
[STRONG] architecture narrowed by multiple independent observations.
[OPEN] raw bytes or vtable target still missing.