# BATCH UPDATE: 0x12B UI consumer -> widget list/value update — 2026-11-19

## Further downstream trace

`FUN_0803E714` does not merely choose a visual label. For object `+0x12B` values 1..4 it builds a concrete parameter/widget list and then resolves every listed parameter through the instance-aware parameter engine.

The relevant sequence is:

1. `FUN_080314BA()` obtains the active module object.
2. `switch(object+299)` has one combined branch for 1,2,3,4.
3. The branch selects a fixed descriptor/data region (`DAT_0803EEC0 + 0x62`) and produces a list of parameter IDs in the UI object at `param_1+0x20`.
4. After list construction, the function loops over those IDs.
5. For each ID it calls `FUN_08036FF2(*(undefined4 *)(param_1+8), parameter_id)`.
6. The returned value is passed to `FUN_0804842C(...)`.
7. `FUN_0804842C` maps the list index to an actual widget record at `param_1 + index*0x338 + 0x42c`, calls `FUN_0804E5BC` to update its value, then `FUN_08032316` to refresh it.

So the proven behavioral path is now:

    +0x12B = 1..4
          |
          v
    FUN_0803E714
          |
          +--> construct Heating parameter list
          |
          +--> FUN_08036FF2(context, parameter_id)
          |        |
          |        +--> +0x12C instance offset
          |        |
          |        +--> concrete CO1/CO2/CO3/CO4 record
          |
          v
    FUN_0804842C
          |
          v
    widget record + index*0x338 + 0x42c
          |
          v
    FUN_0804E5BC + FUN_08032316

This is a real end-to-end firmware path from the object class/instance fields to rendered parameter values.

## Important consequence

The four CO circuits are not implemented as four copies of the UI widget tree. The same UI object/list machinery is reused. The instance dimension changes the parameter lookup result, while the class value selects the Heating UI family.

This is exactly the kind of behavior needed for a 1:1 emulator: preserving the object lifecycle and instance-aware parameter engine is more important than duplicating four static screens.

## Remaining blocker

The parameter IDs used by the 1..4 branch are held in data referenced through `DAT_0803EEC0`/related tables, which the current decompiled text does not materialize. Likewise the vtable/callback entry into `FUN_0803E714` is not emitted as a direct C call. Recovering those data words from Ghidra memory will reveal the exact menu parameter set.

## Next

Continue tracing the indirect constructor/vtable around the 0x3E714 class and recover the data table behind `DAT_0803EEC0`. In parallel continue the C064 indirect-call boundary and `DAT_0803C218` recovery. Do not stop at UI geometry.
