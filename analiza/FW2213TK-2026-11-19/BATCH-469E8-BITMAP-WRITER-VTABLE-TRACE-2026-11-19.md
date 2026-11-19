# BATCH — 469E8 / BITMAP WRITER / VTABLE — 2026-11-19

## 1. [FW] FUN_080307BC is the concrete Bitmap/resource setter

Raw decompiled firmware shows:

    *(undefined2 *)((int)param_1 + 0x26) = *param_2;
    ...
    (**(code **)(*param_1 + 0x38))(param_1, ...);
    (**(code **)(*param_1 + 0x3c))(param_1, ...);

The resource/Bitmap ID is written directly into child +0x26. The helper then obtains resource dimensions and passes them through vtable +0x38/+0x3C.

## 2. [FW] 469E8 gives the exact child and exact writer

Inside FUN_080469E8:

    puVar4 = param_1 + 0x4f;
    FUN_0802df08(puVar4, local_28);
    local_28._0_2_ = 0x0e;
    FUN_080307bc(puVar4, local_28);
    (**(code **)(param_1[0x4f] + 0x2c))(puVar4, ...);
    (**(code **)(param_1[0x4f] + 0x30))(puVar4, 0x14);
    FUN_08030380(param_1, puVar4);

Therefore:

    FUN_080469E8
      -> child @ +0x4F
      -> child +0x26 = 0x000E
      -> resource dimension vtable +0x38/+0x3C
      -> X via +0x2C
      -> Y=20 via +0x30
      -> attach child via FUN_08030380

[STRONG] This is a genuine Bitmap-like TouchGFX child, not merely an arbitrary resource record.

## 3. [FW] vptr of the 469E8 class

The constructor sets the final vptr to DAT_08046CC4.
The actual vtable contents are not materialized as named functions in the exported decompiled C, so no names are invented for its entries.

## 4. [FW] 469E8 geometry is literal firmware geometry

Parent:
    width = 0x46 = 70
    height = 0x96 = 150

Bitmap:
    ID = 14
    Y = 20
    X = centered from parent width and resource width

The four text children have real TypedText IDs and literal geometry.

## 5. [FW] FUN_0803E34C creates four copies

    FUN_080469e8(param_1 + 0x251);
    FUN_080469e8(param_1 + 0x2b8);
    FUN_080469e8(param_1 + 799);
    FUN_080469e8(param_1 + 0x386);

Third offset is decimal 799 = 0x31F. Word offsets produce a fixed byte stride of 0x19C between instances.

[STRONG] Four identical composite instances exist with fixed stride 0x19C.

## 6. [FW] Negative result: no direct dynamic writer found for these four children

In the complete exported decompiled.c, the literal offsets +0x251, +0x2B8, +0x31F and +0x386 occur only in FUN_0803E34C.
There is no statically named/direct decompiled call elsewhere that invokes FUN_080307BC on those four child addresses.

This does NOT prove that the bitmap can never change. Remaining possibilities are indirect/vtable dispatch, parent-level pointer traversal, or a different object/constructor selected by configuration.

Therefore the attack should move from blindly searching for a direct update function to resolving the vtable/indirect dispatch and model binding.

## 7. [STRONG] 370A -> 14 is still NOT proven

Independent hard facts:
    0x370A = Boiler image selector
    RAM = 0x20021FA6
    range = 1..3
    snapshot = 3

and:
    FUN_080469E8 -> Bitmap ID 14 -> 014.png -> 54x100

No direct call-chain 370A -> 11/12/13/14 has been established.

## 8. [STRONG] New best attack

Resolve:
    DAT_08046CC4
      -> vtable entries
      -> methods operating on 469E8 instances
      -> parent/model binding
      -> possible indirect Bitmap/resource selection

In parallel inspect object +0x213 created by FUN_080469D4:
    +0x00 = DAT_080469E4 (vptr)
    +0x04 = parent
    +0x08 = callback/object pointer
    +0x0C = callback/object metadata

This is a plausible bridge between the four visual instances and the active model.

## 9. [CORRECTION]

The previous task wording 'find the writer Bitmap ID' is now closed.
The writer is FUN_080307BC and its exact target field is child +0x26.

The unresolved question is now:

    WHO CALLS FUN_080307BC WITH A VARIABLE RESOURCE ID,
    AND HOW DOES THAT VALUE DEPEND ON THE BOILER VARIANT?

That is the next vertical trace.