# AUTONOMOUS PASS 96 — MENU ROW → RUNTIME CLASS → FIRST-LEVEL HANDLER CLOSURE

## Result
The previously open menu-dispatch subset is closed at the first-level machine dispatch boundary. The runtime class table at 0x20005EF0 is indexed by row; class 0..20 dispatch is already complete in PASS 28. Combining that hard dispatch with the recovered menu semantics closes rows 11..20 without guessing a class as a screen ID.

### Closed mappings
- row 11 = class 11 = Historia alarmów -> 0x080384B0
- row 12 = class 13 = Informacje o programie -> 0x0803850C
- row 13 = class 17 = Konfiguracja -> 0x0803850C
- row 14 = class 15 = Poziom menu/PIN -> 0x08042318 path
- row 15 = class 12 = Język -> special 0x080373BA/0x080373E6
- row 16 = class 14 = immediate return/no-op
- row 17 = class 18 -> 0x08038574
- row 18 = class 16 -> 0x0803856C
- row 19 = class 19 -> 0x08038638
- row 20 = class 20 -> 0x080382EE

## Boundary
This closes row -> class -> first-level handler, not the complete handler -> final page constructor graph. The latter remains a separate static target where the firmware uses common tails, descriptor objects and indirect methods.

## Evidence
PASS 28 provides the complete 21-class TBB dispatch. PASS 39/41 provide runtime row/class semantics and executed language/menu effects. MENUTREE-FULL-CLOSURE provides semantic labels and selector data.

## OPEN carried forward
1. final page constructor/resource chain for classes 11/13/18/19/20;
2. exact second-stage role of selectors and +0x12A/+0x12B for these rows;
3. full widget inventory/callbacks for each final page.
