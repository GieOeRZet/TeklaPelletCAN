# BATCH — 469E8 / ACTIVE-MODULE BOUNDARY — 2026-11-19

## New hard evidence

### 1. FUN_080314BA is the active-module accessor

Independent project traces converge on:

```
FUN_080314BA()
    -> *DAT_08031A8C
```

Therefore the final call in `FUN_080469E8`:

```
uVar1 = FUN_080314BA();
FUN_080318B4(uVar1, param_1);
```

is not a generic UI self-registration guess. The first argument is the currently active module/controller object.

This makes the `469E8` component a model-bound UI object, not merely a static bitmap container.

### 2. This changes the priority of the investigation

The unresolved path is now narrower:

```
active module @ DAT_08031A8C
        |
        v
FUN_080318B4(active_module, 469E8_instance)
        |
        +--> unknown binding/update mechanism
        |
        +--> possible parameter/resource propagation
        |
        v
469E8 child @ +0x4F
        |
        v
Bitmap/resource ID
```

The key question is no longer simply “where is another Bitmap writer?”. The direct constructor writer is already closed:

```
FUN_080307BC(child + 0x4F, 0x000E)
        -> child + 0x26 = 14
        -> resource dimensions via vtable +0x38/+0x3C
```

The remaining problem is whether `FUN_080318B4` or a method reached from the bound module can mutate the bitmap/resource indirectly.

### 3. Four 469E8 instances are probably a coordinated UI group

`FUN_0803E34C` creates four identical `469E8` objects:

- `+0x251`
- `+0x2B8`
- `+0x31F`
- `+0x386`

with fixed stride `0x19C`.

A complete static scan already showed no direct post-construction call to `FUN_080307BC` targeting these four addresses.

Therefore the strongest remaining explanations are:

1. vtable dispatch on the 469E8 object,
2. parent-level traversal,
3. binding/update through `FUN_080318B4`,
4. a model/parameter callback that reaches the object indirectly.

This is stronger than treating the four instances as four independent bitmap constructors.

### 4. +0x213 helper remains a second binding boundary

`FUN_080469D4` creates an object at `+0x213` with:

- vptr = `DAT_080469E4`
- `+0x04` = parent
- `+0x08` = callback/object pointer
- `+0x0C` = callback/object metadata

It does not itself assign Bitmap ID.

This object is therefore a high-value candidate for the bridge between the parent component, active module and the four visual instances.

## Current architecture

```
DAT_08031A8C
    |
    v
FUN_080314BA()
    |
    v
active module/controller
    |
    v
FUN_080318B4(module, 469E8)
    |
    +--------------------------+
    |                          |
    v                          v
469E8 object               +0x213 helper
    |                      DAT_080469E4
    |
    +--> child +0x4F
             |
             +--> Bitmap ID 14 at construction
             |
             +--> 014.png (54x100)

FUN_0803E34C
    |
    +--> 469E8 @ +0x251
    +--> 469E8 @ +0x2B8
    +--> 469E8 @ +0x31F
    +--> 469E8 @ +0x386
```

## What is still NOT proven

- `370A -> 011/012/013/014`
- `370A -> FUN_080318B4`
- `FUN_080318B4` directly changes Bitmap ID
- `+0x213` is definitely the bitmap-selection bridge
- all four 469E8 instances are simultaneously visible

## Next attack

1. Resolve `FUN_080318B4` implementation and all its indirect dispatch.
2. Resolve the object/vtable represented by `DAT_080469E4`.
3. Resolve `DAT_08046CC4` methods and identify any method that reads module/parameter state.
4. Trace fields passed from the active module into `469E8`.
5. Only then return to `0x370A / 0x0801AB7E` and connect the selector if a direct path appears.

## Negative result retained

No direct dynamic Bitmap writer for the four `469E8` instances has been found in the exported `decompiled.c`. This remains an indirect-dispatch problem until raw firmware/vtables are recovered.
