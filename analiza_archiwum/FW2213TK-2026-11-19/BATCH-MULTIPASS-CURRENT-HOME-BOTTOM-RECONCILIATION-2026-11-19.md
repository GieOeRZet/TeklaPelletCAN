# BATCH — MULTIPASS CURRENT CORRECTION / HOME BOTTOM VS 47290 — 2026-11-19

## PASS 1 — reconcile screenshot with firmware geometry

The real screenshot confirms seven visible bottom zones:
1 MENU
2 fuel/hopper
3 burner
4 CO1
5 empty/second heating slot
6 DHW
7 power

However, this visual count is NOT enough to identify the firmware constructors.

Hard firmware geometry for FUN_08047290/FUN_08047334 remains:
- six repeated slots;
- Y ≈ 50, 84, 118, 152, 186, 220;
- therefore the six records are vertically arranged in their local/component coordinates.

[FW] This directly rules out the simple interpretation:
FUN_08047244 + FUN_08047290[6] = seven horizontal bottom-bar tiles.

The screenshot's seven zones therefore remain a separate source-trace problem. The count 1+6 is only structural coincidence until a parent transform/layout/child resource path proves the mapping.

## PASS 2 — hard asset candidate for CO1

The extracted atlas and screenshot agree that:
- 144.png = 41x36;
- 144 is the CO1 active radiator icon;
- the screenshot's fourth bottom zone is CO1.

The repository web implementation maps CO to bitmap/resource 144.

[OPEN] No direct original-firmware FUN_080307BC(..., 0x90) writer call-site has been recovered. Therefore 144 is a confirmed real asset and strong screenshot candidate, but not yet a closed original-firmware resource path.

## PASS 3 — separate right-side control

C33E/C5B4 proves:
- +0x8E0 is a Bitmap child;
- fixed resource = 0x7A = 122;
- X = 398;
- W/H from resource 122 = 35x37;
- Y is runtime-controlled;
- attached through parent+0x04 in the C5B4 layout path.

[STRONG] This is a small right-side UI element, not the bottom CO1 icon.

Do not label it AUTO/60 without direct TypedText/resource/callback proof.

## PASS 4 — current architectural split

Current Home/Main model should therefore be kept as:

FUN_0803E5AC
  -> +0x213D FUN_0802E716 = dynamic content host
  -> +0x23DC FUN_08047244 = separate component
  -> +0x24B7 FUN_08047290 = six-slot vertical list/section
  -> +0x258F FUN_08047604 = large upper component
  -> +0x289B FUN_08047E54 = separate small component
  -> other children

Separately:
FUN_0803C33E
  -> six Bitmap children
  -> +0x85C controlled by 370A
  -> +0x8E0 fixed 122 in C5B4 layout

The screenshot must be reconciled against these real component trees, not by assigning components from the seven-zone count.

## PASS 5 — next highest-value attack

1. Recover the actual firmware construction/writer path for bitmap 144 (resource 0x90).
2. Trace FUN_08047244 child +0x18 to bitmap/TypedText/callback.
3. Trace the six-slot 47290 records to their actual parent geometry and determine why their local Y layout cannot be the observed horizontal bottom bar.
4. Trace the separate bottom-bar component(s) if 47290 is definitively a list/menu elsewhere.
5. Continue C33E/C5B4 hidden-method and sibling analysis in parallel.
6. Only after these paths converge assign MENU/fuel/burner/CO1/CO2/CWU/power to firmware objects.

## CONCLUSION

The real seven-zone screenshot is closed as a visual fact.
The firmware seven-zone architecture is NOT closed.
The old direct mapping of 47244+47290 to the bottom bar remains rejected by hard Y geometry.
Bitmap 144 remains the strongest CO1 asset candidate, but its original firmware writer is still OPEN.
