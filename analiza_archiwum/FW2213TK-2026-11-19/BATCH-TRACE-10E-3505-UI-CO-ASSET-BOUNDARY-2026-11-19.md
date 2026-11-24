# BATCH — 0x10E / 0x3505 → conditional UI → CO asset boundary — 2026-11-19

## PASS 1 — 0x10E fan-out

### [FW] Exact call chain

FUN_08031CCC reads panel index 0x10E through the generic mapper:

```
FUN_08036FF2(context, 0x10E)
        ↓
value_10E
        ↓
FUN_0802D3BC(ui, value_10E > 0, ...)
```

Then it reads the same parameter again:

```
FUN_08036FF2(context, 0x10E)
        ↓
value_10E
        ↓
FUN_0802D3CE(ui, value_10E > 1, ...)
```

Therefore the firmware has a real two-stage threshold fan-out:
- value <= 0: neither conditional element is active,
- value = 1: first active, second inactive,
- value >= 2: first and second active.

### [FW/DATA] 0x10E is panel index 270 and maps to CAN 0x3505

The current parameter map is:
- panel 0x10E -> CAN 0x3505
- panel 0x10F -> CAN 0x2105
- panel 0x110 -> CAN 0x2107
- panel 0x111 -> CAN 0x2106
- panel 0x114 -> CAN 0x2108
- panel 0x115 -> CAN 0x3501

The parameter catalogue identifies 0x3505 as Outside temperature sensor configuration, u8, range 0..2.

### [STRONG] Consequence

The old interpretation "0x10E = number of CO circuits" is rejected.

The code proves only that 0x10E is a 0..2-like configuration value used to activate two UI elements. Its semantic identity is tied by the parameter map to 0x3505, not to the four-instance CO engine.

This is important because the screenshot has a CO1/CO2 bottom-bar arrangement, but the 0x10E branch alone cannot be used as proof that those two tiles are the CO1/CO2 tiles.

## PASS 2 — separation from 0x2105

[FW] The same FUN_08031CCC separately reads panel index 0x10F and sends it to:
- FUN_0802D3E0(ui, value_10F, value_0xDC)
- FUN_0802D91C(ui, value_10F)

Thus:
- 0x10E/0x3505 = two conditional UI elements,
- 0x10F/0x2105 = heating-configuration state/graphic.

No direct 0x2105 -> C064 / +0x12C link has been proven.

## PASS 3 — CO object architecture remains independent

[FW] FUN_0803C064 uses DAT_0803C218[param_2] to select class 1..4 and writes:
- object+0x12B = class/type,
- object+0x12C = instance 1..4.

[FW] FUN_0803E714 consumes class 1..4 through one shared Heating UI branch. Its parameter reads use FUN_08036FF2, which applies +0x12C as the instance offset.

[FW] Four-instance parameter families include:
- 0x2032..0x2035
- 0x2048..0x204B
- 0x2064..0x2067

This is the real CO1..CO4 instance architecture.

## PASS 4 — bitmap atlas / 144 / 146

[DATA] Real extracted assets:
- 144.png = 41x36, active CO1 radiator with number 1.
- 145.png = 41x36, CO1 alternate/inactive.
- 146.png = 43x36, active CO2 radiator with number 2.
- 147.png = 43x36, CO2 alternate/inactive.

[SCREENSHOT] User's real 480x272 screenshot shows:
- bottom zone 4 = CO1 radiator,
- bottom zone 5 = empty in the one-circuit configuration,
- bottom zone 5 can become CO2 when the boiler is configured for two heating circuits.

[OPEN] No hard firmware call-site has yet been recovered that directly writes resource 0x90 (144) or 0x92 (146) through FUN_080307BC.

Therefore 144/146 are semantically confirmed real assets, but their exact firmware widget/resource writer remains OPEN.

## IMPORTANT ARCHITECTURAL RESULT

The current evidence separates two layers that were previously being conflated:

```
0x10E / 0x3505
    -> thresholded UI fan-out (>0, >1)

0x10F / 0x2105
    -> heating configuration state/graphic

CO1..CO4 object layer
    -> class + instance
    -> +0x12B / +0x12C
    -> instance-aware parameter engine
    -> shared Heating UI builder
```

The next trace must therefore find the actual bridge from the conditional UI object(s) to the 144/146 bitmap widgets rather than assuming that 0x10E itself selects CO1/CO2.

## NEXT PASS

1. Recover all caller/context uses of FUN_0802D3BC and FUN_0802D3CE.
2. Recover the exact `ui` object passed by FUN_08031CCC.
3. Trace fields mutated by D3BC/D3CE into Bitmap/TypedText/visibility objects.
4. In parallel trace the real construction/use of resource 144 and 146.
5. Compare the two traces at the parent/widget level.
6. If they do not meet, keep the branches separate and continue through the real CO1/CO2 component constructors.

Do not use geometry alone to force the branches together.
