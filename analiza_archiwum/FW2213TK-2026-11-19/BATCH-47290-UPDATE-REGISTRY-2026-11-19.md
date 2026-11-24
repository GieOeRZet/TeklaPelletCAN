# BATCH — 2026-11-19 — 47290 ALSO ENTERS THE GLOBAL UPDATE REGISTRY

## New hard result

The previously recovered six-slot component `FUN_08047290` is not merely a static six-element container.

Its constructor sequence includes:

```
FUN_0800DCD4(param_1 + 0x8A, DAT_08047330, 0x34, 6)
uVar4 = FUN_080314BA()
FUN_080318B4(uVar4, param_1)
```

Therefore the object built by `FUN_08047290` is registered in the same global timer/update registry already recovered for `FUN_080469E8`.

## Registry architecture already closed

```
FUN_080318B4 = register / retain object
FUN_0803193A = release / unretain
FUN_080317AE = periodic traversal
                  |
                  +-- registered_object->vtable + 0x50
```

Registry:
- object pointers at +0x04 + index*4
- active/reference bytes at +0x68 + index
- count at +0x64
- capacity 0x18

## Consequence for Home

This is important because `FUN_08047290` is a direct child of Home root:

```
FUN_0803E5AC
   +0x92DC
      -> FUN_08047290
           |
           +-- 6-slot structures
           +-- 6 TypedText structures
           +-- FUN_080318B4(active_model, param_1)
           |
           +-- runtime vtable +0x50 update
```

So the six-slot lower-area component has a **real runtime update boundary**.

This strongly changes the next attack: instead of only decoding the six static slots, recover the concrete vtable of the object passed to `FUN_080318B4` and resolve its +0x50 method.

That method is likely where:
- active state,
- visibility,
- selected slot,
- model values,
- or dynamic resource/text updates
are applied.

Do NOT yet claim that +0x50 directly reads CAN or that it maps slots to MENU/palnik/CO/CWU. That requires the method body.

## Parallel comparison

We now have two independently registered Home/UI-family objects:

### Six-slot Home component

```
47290
  -> 318B4
  -> registry
  -> 317AE
  -> vtable +0x50
```

### 469E8 family

```
469E8
  -> 318B4
  -> registry
  -> 317AE
  -> vtable +0x50
```

The common registration path is now a useful fingerprint for locating the actual runtime update method of Home components.

## Next attack

1. Recover the final vptr written by `FUN_08047290`.
2. Resolve that vtable.
3. Read entry +0x50.
4. Follow the +0x50 method until it reaches:
   - a model read,
   - a TypedText/Bitmap setter,
   - visibility,
   - slot selection,
   - or a hard dead-end.
5. Compare its structure against the already recovered 469E8 +0x50 boundary.

This is now higher priority than re-scanning bitmap IDs.

## Confidence

[FW] `FUN_08047290 -> FUN_080318B4(active_model,param_1)`.

[FW] `FUN_080318B4` is the global object register/retain mechanism.

[FW] `FUN_080317AE` dispatches registered objects through vtable +0x50.

[STRONG] `FUN_08047290` therefore participates in dynamic runtime updates, not just static construction.

[OPEN] exact vtable +0x50 implementation for 47290.

[OPEN] semantic mapping of six slots.
