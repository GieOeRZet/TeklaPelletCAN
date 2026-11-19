# TeklaPelletCAN — PERSISTENT CONTINUATION MEMORY
Data: 2026-11-19
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

## PURPOSE
This file is the durable continuation checkpoint. A new chat/agent must treat GitHub as the project memory and continue from the CURRENT START POINT below. Do not restart the investigation from older sections.

## USER OPERATING CONTRACT
- Work in Polish, direct style.
- User expects several deep passes before a report.
- Find -> analyze -> continue -> return to main chain -> repeat.
- A small finding is not a stopping point.
- When a branch is disproven, explicitly correct it and continue from the surviving branch.
- Never fabricate firmware graphics, geometry, class names, vtables, callbacks or semantic labels.
- Do not produce attractive mockups as if they were recovered UI.
- Distinguish evidence: [FW], [DATA], [STRONG], [HYPOTHESIS].
- After a substantial pass, persist the result to GitHub.
- The next chat must start from the last CURRENT START POINT, not from the beginning.

## RAW FIRMWARE
Verified raw copy: FW2213TK_kopia.bin
Correct SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Addressing: runtime = 0x08000000 + raw_offset.

## CLOSED CORE — DO NOT REPEAT
- Panel: 480x272 RGB565.
- Real TouchGFX/Estyma source trace exists: C:\Estyma\igneoTOUCH\app\nasze\igneoTFT\gui\src\components\WheelSelectorExtra.cpp.
- +0x12B = class/type; +0x12C = instance 1..4.
- FUN_08036FF2 physically resolves family-of-4 + instance.
- Record engine: FUN_0801143C / 080115F6 / 0801167A / 080116E6, stride 0x2C.
- +0x12C participates in both READ and WRITE.
- 0x2125 = Device type; 0x3665 = boiler short name; 0x3664 = software version; 0x370A = Boiler image selector.
- 0x3500/3502/350B = hardware/profile layer.
- FUN_0803E5AC is strong Home/Main root candidate; FUN_08047290 creates exactly six repeated objects.
- Home dynamic reads include 0x4005->63.8, 0x215F outside temp, 0x2002/2003/2004 mode/setpoint, 0x3601/3603 fuel.
- 0x0801AB7E is raw data/pixel/table data, NOT the runtime 370A callback.
- Old DAT_08046CC4-as-vtable theory is withdrawn. Its resolved target is UTF-16/resource data.
- Cascade branch is separate: internal 0x158 -> external 0x351A; internal 0x11C -> external 0x350C; these feed FUN_0803E45C -> FUN_08047040 -> 469E8 composites -> fixed Bitmap resource 14.

## CLOSED 370A CHAIN
0x370A
 -> internal 0x121
 -> FUN_08036FF2
 -> mapping table @ 0x08037984
 -> FUN_08037094
 -> FUN_080115F6
 -> record +0x0C
 -> storage 0x20021FA6
 -> u8 value 1..3
 -> FUN_0803CB2C
 -> FUN_0803CACC
 -> +0x85C Bitmap
 -> FUN_080307BC
 -> resource 11/12/13

Therefore:
1 -> resource 11
2 -> resource 12
3 -> resource 13

This is executable-code proof. Do not re-prove or downgrade to hypothesis.

## C33E / C5B4 CLOSED FACTS
FUN_0803C33E constructs six real Bitmap children:
- +0x330
- +0x35C
- +0x85C
- +0x888
- +0x8B4
- +0x8E0
all initialized through FUN_0802DF08 with resource 0xFFFF.

Exactly three direct raw BL callers of FUN_0803C33E exist:
- 08039AD6 from FUN_08039A48
- 08039BBE from FUN_08039B30
- 08039CA6 from FUN_08039C18

These three sibling constructors instantiate the same composite and wire FUN_0803CB04 updater objects.

FUN_0803CB04 = constructor/wiring.
FUN_0803CB2C = runtime update/refresh.
FUN_080307BC = actual Bitmap resource replacement; it writes resource ID and derives W/H through BitmapData/resource registry.

FUN_0803C5B4 is a separate layout/initialization method operating on the same object layout:
- +0x85C at X=40, Y=70
- attaches +0x85C through parent +0x04
- later configures +0x8E0 with resource 0x7A, X=398, Y=runtime, attaches through parent +0x04.

FUN_0804272C is an X/Y setter via object slots +0x2C/+0x30.

C5B4 dispatch remains OPEN: no direct BL and no proven raw function pointer to 0x0803C5B5.

## IMPORTANT CORRECTION — +0x84C
Do NOT call +0x84C the parent/container of +0x85C.

C33E initializes +0x84C separately via FUN_080424C4.
C5B4 attaches +0x85C via parent +0x04.
Therefore current status:
- +0x84C = separate helper/object, semantics OPEN.
- +0x85C = real Bitmap child.
Adjacency does not prove parent/child.

## REAL BITMAP GEOMETRY ALREADY CLOSED
Resource dimensions:
- 11 = 105x126
- 12 = 108x141
- 13 = 82x145
The +0x85C placement is X=40, Y=70 in C5B4.
Derived boxes:
- 11: (40,70)->(145,196)
- 12: (40,70)->(148,211)
- 13: (40,70)->(122,215)
W/H are resource-derived, not invented.

## WHAT IS STILL OPEN
1. Indirect dispatch/method-table path reaching FUN_0803C5B4.
2. Exact semantics/class of +0x84C / FUN_080424C4.
3. All X/Y/W/H/visibility mutations of +0x85C, +0x888, +0x8B4, +0x8E0.
4. Runtime BitmapData/resource records for 11/12/13 and exact mapping to extracted 011.png/012.png/013.png.
5. Which of FUN_08039A48 / 08039B30 / 08039C18 corresponds to the concrete Home/Main boiler screen.
6. Full class/source trace for C33E/CB04 without inventing vtable identity.
7. Role/provenance of fixed resource 14, kept separate from 370A.
8. Exact visibility/state callback behavior around CB04/CB2C.
9. WheelSelectorExtra vptr/class proof.
10. Home six-widget chain: 3E5AC -> 47290 -> vtable/resource/geometry/callback.
11. Heating builder and raw tables, after the current vertical 370A/C33E branch is exhausted.

## CURRENT START POINT — THIS OVERRIDES OLDER HANDOFFS
Start here on the next chat:

### PASS A — C5B4 DISPATCH
Trace all indirect calls/method tables that can reach FUN_0803C5B4. Do not limit the search to BL or literal function-pointer scans. Use surrounding object layout, call sites, vtable-like tables, constructor wiring, and method registration. If no proof exists, keep OPEN.

### PASS B — +0x84C
Decode FUN_080424C4 and identify the exact object semantics from its callers, writes, and method usage. Do not infer container semantics from adjacency.

### PASS C — FULL BITMAP CLUSTER
Enumerate every mutation of:
+0x85C, +0x888, +0x8B4, +0x8E0
including resource ID, X/Y, W/H, visibility, clipping and attachment. Return to the 370A path after every useful subfinding.

### PASS D — RESOURCE REGISTRY
Recover direct BitmapData/resource records for IDs 11,12,13 and correlate them with extracted 011/012/013. No visual guessing.

### PASS E — THREE SIBLINGS
Compare FUN_08039A48 / 08039B30 / 08039C18 after the common C33E call and upstream/downstream wiring. Identify screen semantics only when backed by hard/strong evidence.

### PASS F — ONLY THEN RENDER
No render before enough real asset + real geometry + parent/visibility evidence exists.

## CONTINUATION RULE
When the above is exhausted, continue into:
C33E/CB04 source trace -> Home root -> six widgets -> WheelSelectorExtra -> heating builder -> raw tables -> identity/profile, always preserving the evidence labels.

## LAST CONSOLIDATED COMMITS BEFORE THIS MEMORY FILE
- latest MASTER before this checkpoint: 972e39e85170e8c821cf60eaa96a2b6410d41dd4
- latest batch before this checkpoint: 2551d0b130ba5b051d3bb6ab103d9878ffb5f344
