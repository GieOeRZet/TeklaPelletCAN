# FW2213TK — CO2 UI: concrete widget geometry + vtable boundary — 2026-11-19

## Major consolidated result

[FW] The CO2 UI component has now been tied to a concrete internal widget set and real screen geometry.

### Component / vtable
CO2:
- raw component: `0x46D2C`
- runtime/Ghidra: `0x08056D2C`
- vtable raw `0x7EE20`
- vtable entries include:
  - +0x00 -> `0x08043A33`
  - +0x04 -> `0x08056D2D`
  - +0x08 -> `0x080A60EB`
  - +0x0C -> `0x080570F5`
  - +0x10 -> `0x08043C73`
  - +0x14 -> `0x08043E3B`
  - +0x18 -> `0x08043F39`
  - +0x1C -> `0x080570F7`
  - +0x20 -> `0x080A60ED`
  - +0x2C -> `0x0809DE09`
  - +0x34 -> `0x08043A33`
  - +0x38 -> `0x0805B33D`
  - +0x3C -> `0x080A60EB`
  - +0x40 -> `0x0805B4D1`

CO1:
- raw component: `0x4B618`
- runtime/Ghidra: `0x0805B618`
- vtable raw `0x7F778`
- same common skeleton but different implementation entries, including +0x04 -> `0x0805B619`.

[STRONG] CO1 and CO2 are distinct firmware UI class variants, not merely one widget with a different caption.

## Concrete widget rectangles

[FW] The component contains at least these two real UI objects:

| object | TypedText | text | X | Y | W | H |
|---|---:|---|---:|---:|---:|---:|
| `r4+0x8B4` | 348 | Błąd wygaszania | 205 | 195 | 200 | 70 |
| `r4+0x8EC` | 460 | Liczba kotłów slave | 320 | 195 | 200 | 70 |

These are decoded from actual geometry arguments to the firmware's geometry helper, not visual guesses.

[STRONG] The two rectangles overlap horizontally (205..405 and 320..520) and extend below the nominal 480-wide screen in the second case. Therefore they are **not automatically interpreted as simultaneously visible final-screen fields**. They are likely alternative/conditional objects or belong to a larger coordinate context; visibility/parent clipping must still be resolved.

## Screen-sized child

[FW] In `0x080612E0`:
- `r0 = this + 0x48`
- X=0
- Y=0
- W=480
- H=272
- call `0x08030358`

[FW] `0x08030358` is the reusable geometry helper with convention:
`r0=object, r1=X, r2=Y, r3=W, stack=H`.

[HYPOTHESIS] `this+0x48` is a screen/root-like child. Do not name it Root/Screen until vptr and parent-child insertion are recovered.

## Critical correction

[CORRECTION] `+0x12B` is **not** the CO instance selector. In `0x0805D948` it selects a broader UI/device type and TypedText branch. The parameter-engine instance selector remains `+0x12C`.

## Critical methodological correction

[FW] raw `0x46D3C` contains a real Thumb-2 BL to runtime `0x0805D948`, although Ghidra's `functions.txt` does not list `0x0805D948` as a function start.

Therefore:
- do not rely exclusively on `functions.txt`;
- scan raw BIN for executable BL targets;
- especially inspect UI regions where Ghidra failed to split constructors.

## Current architecture model

```
CO2 component 0x08056D2C
  |
  +-- accessor 0x080414BA
  |     -> global object 0x20024814
  |     -> +0x12A = 2
  |
  +-- BL 0x0805D948
        |
        +-- BL 0x080612E0
        |     |
        |     +-- child +0x48 -> 0,0,480,272
        |     |
        |     +-- further UI construction
        |
        +-- +0x12B -> UI/device type selector
        |
        +-- widgets at +0x8B4 / +0x8EC
              |
              +-- TypedText 348 / 460
              +-- real geometry
```

This is now the first useful concrete TouchGFX-style object graph fragment.

## Next attack

1. Recover the **vptr write** for `this+0x48`.
2. Resolve the class behind geometry helper's vtable slots +0x34/+0x38/+0x3C.
3. Resolve what creates/initializes objects at `+0x8B4` and `+0x8EC`.
4. Find visibility/setVisible calls for these two widgets.
5. Find parent-child/add() calls.
6. Trace the dynamic value associated with TypedText 348/460 into the parameter engine.
7. Then connect the object instance selector +0x12C to CO1/CO2 CAN indices.

## Do NOT repeat

- count=4 / CO1+1 family proof;
- generic TouchGFX identification;
- bitmap extraction;
- 480x272 framebuffer discovery;
- +0x12B vs +0x12C distinction;
- 63.8 modulation chain;
- old 0x2105-as-CO-counter hypothesis.

## Confidence

[FW] Real CO2 component and separate CO1 vtable.
[FW] Real widget offsets +0x8B4/+0x8EC.
[FW] TypedText 348/460.
[FW] Exact rectangles 205,195,200,70 and 320,195,200,70.
[FW] Screen-sized child +0x48 = 0,0,480,272.
[STRONG] This is a concrete UI object graph fragment.
[HYPOTHESIS] Exact TouchGFX class names and parent hierarchy remain unresolved.
