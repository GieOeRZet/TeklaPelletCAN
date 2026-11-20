# HOME GEOMETRY — USER VISUAL CORRELATION — 2026-11-20

## Ground-truth observations from physical/UI observation

These observations must override speculative semantic labels when correlating firmware objects with the visible main screen.

### 1. The six-slot geometry from FUN_08047290 is NOT visible on the Home screen

Previously recovered firmware geometry:
- (100,50)
- (100,84)
- (100,118)
- (100,152)
- (100,186)
- (100,220)

User confirms that there is no vertical six-item menu/list on the visible Home screen.

Therefore:
- do NOT label this component as a Home vertical menu;
- do NOT force these six coordinates into the Home layout;
- investigate it as a different screen/component;
- possible hypotheses include update-language selection or another firmware/update/configuration screen, but this remains OPEN;
- the hypothesis that the six slots are generated vertically and later rotated 90 degrees is currently unsupported and should not be assumed.

The fact that the uploaded BIN is itself an update firmware is relevant context, but it does not prove the six-slot component is language selection. Language count also does not match a simple six-language interpretation. This is OPEN until constructor/factory/event path identifies the screen.

### 2. Bitmap 115 is confirmed by physical UI observation

Bitmap/resource 115 = the lower-right Home-screen tile:
- settings / menu / power-related button.

This is user-observed correspondence.

### 3. Bitmap 144 is confirmed

Bitmap/resource 144 = CO1 icon used on the Home-screen tile.

### 4. Bitmap 174 is confirmed

Bitmap/resource 174 = CWU icon used on the Home-screen tile.

## Consequence for firmware-only reconstruction

The previous negative-evidence result for direct immediate loads of 115/144/174 must NOT be interpreted as evidence that these resources are absent from Home.

They are now externally confirmed as Home-screen resources.

Therefore the next firmware attack must trace their indirect/table-driven resource resolution:
- bitmap table entry
- resource/object constructor
- Home tile constructor
- parent geometry
- runtime selection/update path
- touch/callback target.

## Strong separation rule

There are now two evidence classes:

1. HARD FIRMWARE:
   coordinates, resource IDs, constructor calls, parent links, setters, tables.

2. USER VISUAL CORRELATION:
   confirmed semantic identity of resource 115/144/174 on the real Home screen.

When the two are combined, the goal is to find the firmware path that produces the observed Home tiles, not to reinterpret the observed screen to fit an unrelated constructor.

## Immediate next targets

1. Find every indirect use of bitmap/resource 115.
2. Find every indirect use of 144.
3. Find every indirect use of 174.
4. Cluster those uses by parent constructor.
5. Recover tile X/Y/W/H from the same parent path.
6. Identify the lower-right tile containing 115.
7. Identify the CO1 and CWU tile containers containing 144 and 174.
8. Trace neighboring Home tile resources to reconstruct the complete tile grid.
9. Independently locate the firmware route that constructs the visible Home screen.
10. Reclassify 08047290 after its factory/caller is identified.

No geometry from old HA/card projects is to be used as proof.
