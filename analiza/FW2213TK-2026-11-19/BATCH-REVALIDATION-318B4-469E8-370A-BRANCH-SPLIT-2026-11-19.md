# BATCH — REVALIDATION: 318B4 TIMER REGISTRY / 469E8 / 370A BRANCH SPLIT — 2026-11-19

## Executive result
This multipass re-run corrected the previously assumed edge 370A -> FUN_080318B4 -> 469E8.
FUN_080318B4 is a timer/update-widget registration and reference-count function. It does not read a parameter, CAN index, model value, bitmap ID or resource ID.
The actual runtime update boundary is FUN_080317AE, which dispatches each registered object's vtable slot +0x50.

## Pass 1 — FUN_080318B4
Exact semantics:
- widget count at object +0x64;
- widget pointers at +0x04 + index*4;
- active/reference bytes at +0x68 + index;
- maximum 0x18 entries;
- existing objects increment a reference byte.
Therefore registration is not the model binding/update itself.

## Pass 2 — FUN_080317AE
FUN_080317AE contains the decisive indirect dispatch:
registered_widget -> vtable +0x50 -> actual per-update method.
This is the correct next boundary for the 469E8 object.

## Pass 3 — FUN_080469E8
FUN_080469E8 installs DAT_08046CC4 as vptr, constructs the Bitmap child at +0x4F, and calls FUN_080307BC(child +0x4F, 0x0E).
Thus Bitmap/resource ID 14 is a hard constructor fact.
The constructor then obtains FUN_080314BA() and registers itself with FUN_080318B4.
No direct model read occurs in the constructor.

## Pass 4 — negative writer scan
Complete exported decompiled.c scan found no second hard-coded FUN_080307BC writer with resource IDs 0x0B, 0x0C or 0x0D.
The relevant 469E8 constructor has the 0x0E case.
Therefore 370A -> bitmap 11/12/13/14 is still NOT proven.

## Pass 5 — Home parent updater
FUN_0803E45C is a genuine model-driven Home update path. It reads model values through FUN_08036FF2 for indices 0x11C, 0x157, 0x154, 0x153, 0x156, 0x155, 0x158, 0x0C, 0x31..0x37 and 0x14D..0x150.
It does not directly read 370A.
So FUN_0803E45C is a real model/UI spine, but the 370A edge is not closed there.

## Pass 6 — active-module +0x158
FUN_080314BA() returns the global active/module object used throughout the UI.
That object contains state fields such as +299 and +0x158.
FUN_08037E74 maps input values 0, 900, 999 and 0x1BF1 to +0x158 values 0..3.
This is a real selector/state mechanism, but it must NOT be relabeled as 370A without a direct data chain.

## Pass 7 — FUN_0803E714
FUN_0803E714 reads active-module +299 and repeatedly tests +0x158 while constructing a UI/model list.
This confirms a second state-driven UI path, but again it does not establish 370A -> +0x158.

## Corrected architecture
PARAMETER TABLE -> 0x370A -> RAM 0x20021FA6 -> callback boundary 0x0801AB7E -> UNKNOWN HANDLER / NOTIFICATION

Separately:
MODEL / ACTIVE STATE -> Home update functions -> parent -> four 469E8 objects -> fixed Bitmap ID 14
and
469E8 -> FUN_080318B4 registration -> FUN_080317AE -> vtable +0x50 -> UNKNOWN runtime update.

## Critical correction
The earlier statement that FUN_080318B4 is the active-module binding/update boundary is too strong.
Correct statement: FUN_080314BA obtains the global active/module object; FUN_080318B4 registers a widget in its timer/update registry; FUN_080317AE later dispatches the registered object's vtable +0x50 method.

## Next attack
1. Recover raw Thumb2 around 0x0801AB7E and determine what it reads/writes and which notification path it enters.
2. Recover DAT_08046CC4 vtable slot +0x50 and trace that function completely.
3. Find all model reads corresponding to the state stored at RAM 0x20021FA6.
4. Only after A/B/C merge the 370A path with the concrete Home widget.
5. Do not infer 370A=1/2/3 -> bitmap 011/012/013/014 from asset numbering.

## Bottom line
318B4 = registration; 317AE = runtime dispatch; +0x50 = real widget update boundary; 469E8 = fixed Bitmap 14 at construction; 370A = upstream callback at 0x0801AB7E.
This is a branch split, not a dead end. The next breakthrough requires two independent recoveries: 0x0801AB7E and DAT_08046CC4 + 0x50.