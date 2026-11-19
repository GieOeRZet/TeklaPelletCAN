# BATCH: Heating UI class branch and hidden mode gate — 2026-11-19

## New consolidated findings

### 1. `FUN_0803E714` uses a fixed 12-entry parameter list for object classes 1..4

The branch for `+0x12B == 1,2,3,4` calls:

`FUN_0803EFDA(param_1, DAT_0803EEC0 + 0x62, 0x0C)`

`FUN_0803EFDA` simply copies `param_3` consecutive 16-bit parameter IDs into the UI object's list at `param_1+0x20`, then increments the count at `+0xE8`.

Therefore the Heating class 1..4 branch has an explicit **12-parameter base menu**. If object state `+0x158 != 0`, it appends another 11 entries from `DAT_0803EEC0 + 0x6E` and sets the secondary count to 11.

The exact numeric parameter IDs cannot be recovered from the current decompiled text because the contents of `DAT_0803EEC0` are not emitted.

### 2. `+0x158` is NOT the CO instance field

`FUN_08037E74(param_1,param_2)` maps a separate input value:

- 0 -> `+0x158 = 0`
- 900 -> `+0x158 = 1`
- 999 -> `+0x158 = 2`
- 0x1BF1 -> `+0x158 = 3`

The function has no direct C callers in the decompiled output, so this is another indirect-dispatch/data boundary. It is a separate mode/variant gate used throughout the UI.

Thus the Heating branch has two orthogonal dimensions:

- `+0x12B` = object/class selection, with 1..4 selecting the Heating/CO family
- `+0x12C` = instance selection used by the parameter engine
- `+0x158` = separate UI/variant mode controlling whether additional parameter groups are appended

This prevents incorrectly interpreting the optional 11 entries as CO2..CO4 selection.

### 3. Exact runtime path is now clearer

For classes 1..4:

`DAT_0803C218[param_2] -> 1..4 -> +0x12B/+0x12C -> FUN_0803E714 -> 12 base parameter IDs -> FUN_08036FF2(id, instance) -> widget value`

If `+0x158 != 0`, the same class branch adds an additional 11-parameter group before the instance-aware lookup loop.

### 4. Exact memory export needed to eliminate current data-table blockers

To recover the actual parameter IDs, the useful Ghidra memory/data export is the region beginning at `0x0803EEC0`. The largest offsets used by the nearby UI builder reach roughly `+0x9C`, and the next related table starts at `DAT_0803F008`.

A raw memory dump covering approximately:

`0x0803EEC0 .. 0x0803F008`

with bytes/halfwords and labels preserved would resolve the Heating menu's exact parameter-ID list.

The separate `DAT_0803C218` 108-byte classification table remains the critical missing input for mapping `param_2 -> class 1..4`.

## Next attack

1. Continue tracing the indirect source of `FUN_08037E74` and identify what generates 900/999/0x1BF1.
2. Continue the indirect C064 entry and recover `DAT_0803C218`.
3. Trace `FUN_0803EB4A` and its `DAT_0803F008` metadata table to determine what each Heating parameter ID means once the IDs are available.
4. Keep the 0x2105..0x2108 link unclaimed until an actual data/code path proves it.
