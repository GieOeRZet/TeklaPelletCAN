# FW2213TK — UI/CO2 chain: screen-sized child and geometry boundary — 2026-11-19

## Status
This note consolidates the next structural result after the TouchGFX handoff. It does **not** restart the firmware analysis.

## 1. Confirmed chain

[FW] The already recovered CO2 component begins at raw `0x46D2C`, runtime/Ghidra `0x08056D2C`.

The chain recovered from direct firmware disassembly is:

```
CO2 component @ raw 0x46D2C / runtime 0x08056D2C
    |
    +-- BL 0x080414BA
    |      -> accessor of global object pointer at RAM 0x20024814
    |
    +-- object + 0x12A = 2
    |
    +-- BL 0x0805D948
             |
             +-- object + 0x12B is read
             +-- type-dependent TypedText selection
             |
             +-- BL 0x080612E0
                      |
                      +-- child = this + 0x48
                      +-- setGeometry(child, 0, 0, 480, 272)
                      +-- additional UI/object setup
```

The important point is that the 480x272 object is **not merely an independent display-size fact**. It is created/configured from inside the chain entered by the CO2 component.

## 2. Geometry helper is now a fixed primitive

[FW] `0x08030358` is the common geometry helper.

Its caller convention is:

```
r1 = X
r2 = Y
r3 = W
stack = H
```

and it dispatches to object vtable slots +0x34/+0x38/+0x3C.

[STRONG] Therefore every call already recovered through `0x08030358` can be converted directly into a real UI rectangle:

`object -> X,Y,W,H`.

Independent firmware evidence gives `0,0,480,272` for `this+0x48` in `0x080612E0`.

This supersedes the older state that treated the four geometry arguments as unresolved.

## 3. What the 480x272 child means

[FW] `0x080612E0` is a real Ghidra function (224 B) and is reached from `0x0805D948`.

[STRONG] The child at `this+0x48` is therefore a screen-sized UI object nested in the larger component/constructor chain. It is not justified to call it the global TouchGFX root yet.

The safest current model is:

```
larger UI component
  └── child +0x48
        └── geometry 0,0,480,272
        └── further TouchGFX-style configuration
```

Do **not** rename this child to `Screen`, `root`, or `background` until its vptr/add-to-hierarchy path is recovered.

## 4. Type field correction

[FW] In `0x0805D948`, the byte at object +0x12B selects a TypedText branch. The recovered mapping includes:

- 0 -> TypedText 40 = BIG
- 1 -> TypedText 42 = STD
- 2 -> TypedText 43
- 3 -> TypedText 44
- 4 -> TypedText 45
- 5 -> TypedText 46
- 6 -> TypedText 49
- 7 -> TypedText 47
- 8 -> TypedText 161 = Test pompy
- 9 -> TypedText 48
- 10 -> TypedText 41 = MINI
- >10/default -> TypedText 161

[STRONG] This definitively prevents interpreting +0x12B as simply “CO number”. It is a broader object/device type selector.

The actual CO instance mechanism remains +0x12C in the parameter engine.

## 5. CO1/CO2 component distinction

[FW] Two separate UI code bodies were recovered:

- raw `0x46D2C` / runtime `0x08056D2C` -> TypedText 58 = “Ogrzewanie 2”
- raw `0x4B618` / runtime `0x0805B618` -> TypedText 57 = “Ogrzewanie 1”

Their vtable layouts are similar but not identical.

[STRONG] These are real separate component implementations, not merely two uses of the same text resource.

This is the current bridge between “screen semantics” and “object implementation”.

## 6. Important negative result

No new direct proof was found that `0x2105` calls C064 or directly creates CO objects.

Do not reintroduce:

`0x2105 -> C064`

as a fact.

The confirmed independent chains remain:

```
0x2105 -> FUN_08036FF2 -> FUN_0802D3E0 / FUN_0802D91C -> Heating UI state
```

and:

```
C064(param_1,param_2)
 -> DAT_0803C218[param_2]
 -> class/type
 -> +0x12B/+0x12C
 -> instance-aware parameter engine
```

The missing bridge is still the indirect caller/function-pointer path into C064.

## 7. Corrections to preserve

[CORRECTION] Do not use the old synthetic `0x08046D2C` as the runtime/Ghidra address. It means raw `0x46D2C`.

For this firmware:

- raw offset = byte position in BIN
- runtime/Ghidra code address = `0x08010000 + raw`
- therefore raw `0x46D2C` = runtime `0x08056D2C`
- raw `0x4B618` = runtime `0x0805B618`
- raw `0x4D948` = runtime `0x0805D948`

Do not apply the +0x10000 correction to the old code model indiscriminately; the established handoff already separates code space from asset/text pointer space.

## 8. Next attack — concrete, not generic

Priority is now the **object hierarchy boundary**, not another register scan.

### A. Resolve `0x080612E0` callees from its actual call convention
Especially:
- `0x080313A4`
- `0x080314BA`
- `0x08030358`
- `0x0804272C`
- `0x080347DC`

Determine for each:
- what object is passed,
- whether it is a TouchGFX TextArea/Container/Image-like object,
- which fields/vptr are touched,
- whether it adds a child or only configures one.

### B. Resolve the vptr of `this+0x48`
Do not infer the class from the size or geometry. Find:
- constructor/vptr write,
- vtable address,
- methods used by +0x34/+0x38/+0x3C,
- parent/child add path.

### C. Trace `0x0805D948` upward
Find the object that owns the CO2 component and the call which inserts it into the surrounding UI hierarchy.

Target chain:

```
Home/Main screen
 -> parent
 -> CO2 component @ 0x08056D2C
 -> owner object
 -> child +0x48
 -> concrete widget classes
 -> TypedText/Bitmap
 -> update callback
 -> panel parameter
 -> instance
 -> CAN
```

### D. Only after A-C
Return to C064 and recover the missing:
`param_2 -> DAT_0803C218 -> class 1..4`.

## 9. Do NOT repeat

- Bitmap extraction: already done.
- Generic TouchGFX framework identification: already done.
- Count=4 proof: already done.
- +0x12B/+0x12C distinction: already done.
- 0x2105 vs 0x3505 separation: already done.
- 63.8 formatting: already done.
- Geometry helper identification: now fixed as a reusable primitive.

## Confidence

- [FW] CO2 component -> 0x0805D948 -> 0x080612E0.
- [FW] 0x080612E0 creates/configures child +0x48 with 0,0,480,272.
- [FW] 0x08030358 receives X,Y,W,H in that order.
- [FW] +0x12B selects broader type/device UI text; it is not simply CO number.
- [STRONG] CO1 and CO2 are separate UI component implementations.
- [STRONG] The next missing UI boundary is object/vptr/parent-child hierarchy.
- [HYPOTHESIS] child +0x48 is a screen/root-like TouchGFX object; do not implement this assumption until vptr/hierarchy confirms it.

## Continuation for next agent

Start here, not from the master beginning:

`0x08056D2C -> 0x0805D948 -> 0x080612E0`

Resolve the five helper callees and the vptr of `this+0x48`. The desired output is the first concrete TouchGFX class/parent-child chain with at least one real X/Y/W/H + TypedText/Bitmap relation.