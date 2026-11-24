# CORRECTION — 47290 IS VERTICAL LIST, NOT LOWER AREA — 2026-11-19

## Mandatory semantic correction

The previous batch `BATCH-47290-UPDATE-REGISTRY-2026-11-19.md` correctly established that `FUN_08047290` registers itself with `FUN_080318B4`, but its wording called it a "lower-area component". That wording is withdrawn.

Hard geometry from `FUN_08047334`:

- six visual records
- six TypedText records
- Y positions approximately 50, 84, 118, 152, 186, 220 px

Therefore `FUN_08047290` is a **vertical six-item list/menu/selector-like component**, not the horizontal bottom bar.

Do not use 47290 as evidence for the bottom bar.

## What remains valid

The runtime/update conclusion remains valid:

```
FUN_08047290
  -> FUN_080318B4(active_module, param_1)
  -> global update registry
  -> FUN_080317AE
  -> registered_object vtable + 0x50
```

Thus the next technical question for 47290 remains its concrete vtable +0x50 method, but its UI role must be described only as a vertical six-item component until semantic evidence identifies it.

## Current Home role map

```
FUN_0803E5AC
 |
 +-- 0802E716  = content/host container; NOT boiler bitmap
 +-- 08047244  = separate component; resource/child still to identify
 +-- 08047290  = vertical 6-item list; NOT bottom bar
 +-- 08047604  = graph/chart component; NOT boiler bitmap
 +-- 08047E54  = small composite; uses resources 0x1B6..0x1B9; NOT boiler 011..014
 +-- 08038ED0 / other children = unresolved
```

## Boiler-image path status

The hard boiler-image spine remains separate:

```
370A
 -> RAM 0x20021FA6
 -> value 1..3
 -> unresolved handler boundary 0x0801AB7E

and independently:

469E8 / sibling family
 -> runtime Bitmap mechanism
 -> known bitmap resources 11..14 in related structures
```

The missing merge is still the variable resource writer that turns the configuration value into the actual Home boiler bitmap.

## Next attack

Do not spend another pass re-proving 47290 geometry.

Priority is now:

1. `FUN_0802E716` child/resource chain, especially `FUN_08034A90` and `FUN_08034D74`.
2. `FUN_08047244` exact child/vptr/resource.
3. Home sibling objects `08047FD4/FE8/FFC` and `0802DF08`.
4. Resolve `0x0801AB7E` only when the raw/code path becomes available.
5. Compare every candidate against the actual bitmap resource IDs 011..014.

## Rule

A component is not assigned to a screenshot region from element count alone. Require geometry + resource/TypedText, or geometry + callback/model evidence.
