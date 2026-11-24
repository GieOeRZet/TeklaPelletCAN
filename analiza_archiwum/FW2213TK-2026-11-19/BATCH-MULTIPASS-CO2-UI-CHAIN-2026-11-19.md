# BATCH — MULTIPASS CO2 / UI OBJECT CHAIN — 2026-11-19

## Cel
Kontynuacja reverse-engineeringu bez restartu. Ten przebieg łączy odzyskany komponent CO2 z konkretnym drzewem widgetów i oddziela twarde fakty od hipotez.

## PASS 1 — CO2 class/object boundary

[FW]
- CO2 component: raw 0x46D2C, Ghidra/runtime 0x08056D2C.
- CO1 component: raw 0x4B618, Ghidra/runtime 0x0805B618.
- CO2 i CO1 mają różne vtable:
  - CO2 vtable raw 0x7EE20.
  - CO1 vtable raw 0x7F778.
- CO2 posiada +0x12A = 2.
- CO1 posiada analogiczną własną strukturę.
- +0x12B NIE jest numerem obwodu CO; w runtime 0x0805D948 wybiera TypedText zależnie od typu/urządzenia (m.in. BIG/STD/MINI/Test pompy).
- +0x12C pozostaje instancją używaną przez parameter engine.

## PASS 2 — concrete constructor chain

[FW]
CO2:
0x08056D2C
 -> BL 0x080414BA
 -> global object pointer *0x20024814
 -> object +0x12A = 2
 -> BL 0x0805D948
 -> BL 0x080612E0

0x080414BA is accessor, not constructor:
 -> reads pointer from RAM 0x20024814 and returns it.

0x0805D948 is a real BL target although not registered by Ghidra as a function start.

## PASS 3 — 0x080612E0 concrete UI geometry

[FW]
FUN_080612E0 = 224 B.

It calls:
0x080393B2
0x08030354
0x08030358
0x08039474
0x080307BC
0x080314BA
0x08027DEC
0x080313A4
0x08039424
0x08031426
0x0804272C
0x080347DC
0x0803A0F8

Concrete geometry:
this + 0x48 -> X=0, Y=0, W=480, H=272 via FUN_08030358.

FUN_08030358 is proven setGeometry(object,X,Y,W,H).

FUN_080313A4(object, typedTextId) is a TypedText setter/configurator:
- CO1 uses object r4+0xA4, id 0x39 = TypedText 57 = "Ogrzewanie 1".
- CO2 uses object r4+0xA4, id 0x3A = TypedText 58 = "Ogrzewanie 2".

FUN_080314BA is active-model accessor:
 -> *DAT_08031A8C.
Do not classify it as a widget constructor.

FUN_0804272C is a two-coordinate X/Y setter:
 -> object slot +0x2C gets r1
 -> object slot +0x30 gets r2.

## PASS 4 — CO2 internal widgets

[FW]
Within the CO2 component, real widgets exist at:
- r4+0x8B4 -> TypedText 348 "Błąd wygaszania", geometry X=205 Y=195 W=200 H=70.
- r4+0x8EC -> TypedText 460 "Liczba kotłów slave", geometry X=320 Y=195 W=200 H=70.
- r4+0x85C -> TypedText 68 "Moc 2" (from the direct raw constructor trace).

The 8B4 and 8EC rectangles overlap and the second extends beyond x=480. Therefore they must NOT be assumed simultaneously visible final-screen fields. Visibility/parent clipping remains OPEN.

## PASS 5 — bottom-bar architecture cross-check

[FW]
Home root candidate FUN_0803E5AC has:
- FUN_08047244 = separate component with child +0x18 and own vptr.
- FUN_08047290 = exactly 6 repeated slots, each with visual child + TypedText + geometry/color/children through FUN_08047334.

This gives a structural 1+6 = 7-zone lower area matching the observed screenshot partition.

[OPEN]
Do not assign slot 0..5 to MENU/fuel/burner/CO1/CO2/CWU/power until bitmap/text/callback trace closes the mapping.

## Critical exclusions
- Do not revive 0x10E as CO circuit count. It maps to CAN 0x3505 and has a separate thresholded UI fan-out.
- Do not treat +0x84C as parent of +0x85C; it is a separate helper/object initialized by FUN_080424C4.
- Do not call +0x8E0 resource 122 an AUTO icon without direct proof.
- Do not use 47290[6] alone as proof of specific bottom-bar labels.
- Do not rely on functions.txt alone; raw BL targets can exist at unregistered function boundaries.

## Next attack
1. Recover exact call convention and object offsets for all 0x080612E0 callees.
2. Resolve visibility/add-parent chain for CO2 widgets 0x85C/0x8B4/0x8EC.
3. Trace CO2 vptr assignment from raw PC-relative stores.
4. In parallel, trace 47244 and 47290/47334 bitmap/resource IDs and callbacks.
5. Return to 0x10E -> D3BC/D3CE only after concrete object targets are recovered.
