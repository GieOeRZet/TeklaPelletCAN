# HOME / MAIN-SCREEN GEOMETRY — FW-ONLY MULTIPASS AUDIT — 2026-11-20

Source: uploaded `FW2213TK_kopia.bin`
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
Size: 2,031,616 bytes
Firmware address base used: `0x08010000`

## Scope

This pass intentionally treats the uploaded firmware as the primary evidence. Existing HA/card geometry from older project work is NOT used as proof.

The analysis was split into multiple independent tracks:
1. screen/factory topology,
2. direct object-tree reconstruction,
3. geometry-setter callsite extraction,
4. child-constructor recursion,
5. bitmap/resource setter tracing,
6. TypedText table recovery,
7. hopper bitmap update tracing,
8. six-slot selector geometry,
9. large graphic-layer geometry,
10. boiler-widget geometry,
11. text-widget geometry,
12. generic widget/base-constructor geometry,
13. screen-resolution/full-frame geometry scan,
14. parent/child attachment tracing,
15. dynamic-coordinate source tracing,
16. negative-evidence scan for hardcoded Home bitmap IDs,
17. separation of visual objects from model/configuration helpers,
18. cross-check against independent call paths,
19. root/factory ambiguity audit,
20. final evidence classification.

## 1. Critical correction

`FUN_0803E5AC` has a genuine large object tree, but the firmware alone does NOT justify calling every object in that tree a visible Home widget.

The tree contains parameter/configuration/error-language-heavy children. Therefore:
- tree topology = HARD,
- individual child semantics = mixed,
- visible Home composition = still partially OPEN.

In particular, the earlier interpretation that `0803E5AC` is itself a simple literal Home renderer is too strong. It is better classified as a large runtime screen/model host.

## 2. Hard direct tree of 0803E5AC

Direct child/helper construction is:

- root + `0x380` -> `FUN_08038ED0`
- root + `0x3BC` -> `FUN_08041E1C`
- root + `0x3EC` -> `FUN_08041E1C`
- root + `0x41C` -> `FUN_08047230`
- root + `0x42C` -> repeated `FUN_0800DCD4` records, stride `0x338`, count `0x28`
- root + `0x84F4` -> `FUN_0802E716`
- root + `0x8F70` -> `FUN_08047244`
- root + `0x92DC` -> `FUN_08047290`
- root + `0x963C` -> `FUN_08047604`
- root + `0xA26C` -> `FUN_08047E54`
- root + `0xA5FC` -> `FUN_08038ED0`
- root + `0xA628` -> `FUN_08038ED0`
- root + `0xA654` -> bitmap/resource object `FUN_0802DF08`
- root + `0xA680` -> bitmap/resource object `FUN_0802DF08`
- root + `0xA6AC` -> `FUN_08047FD4`
- root + `0xA6BC` -> `FUN_08047FE8`
- root + `0xA6CC` -> `FUN_08047FFC`
- root + `0xA6DC` -> `FUN_08047FE8`

The child-link helper is `FUN_08030380`.

## 3. Hard geometry: full-frame geometry exists in firmware

The firmware contains direct geometry calls of the form:

`FUN_08030358(object, x, y, width, height)`

A proven full-frame example is in `FUN_0802C294`:

- X = 0
- Y = 0
- W = 480
- H = 272

Therefore the firmware's UI coordinate space is directly proven to contain a 480×272 full-frame widget.

Important: this proves the coordinate system, but `0802C294` is a parameter/configuration-heavy component and must NOT be mislabeled as the literal Home screen merely because it owns a full-frame background.

## 4. 47290 — hard geometry

`FUN_08047290` is a vertical six-slot component.

Its records:
- first record: object + `0xA8`
- stride: `0x40`
- six records.

The update function `FUN_08047334` sets:
- X = 100
- Y = 50 + 34×slot

Therefore:

| slot | X | Y |
|---:|---:|---:|
| 0 | 100 | 50 |
| 1 | 100 | 84 |
| 2 | 100 | 118 |
| 3 | 100 | 152 |
| 4 | 100 | 186 |
| 5 | 100 | 220 |

This is hard firmware geometry.

The same component uses bitmap resources:
- 151 = normal state
- 152 = selected state

The labels are supplied dynamically from a TypedText-ID array, so the six labels are configuration-dependent.

## 5. 47604 — large central graphic region

`FUN_08047604` creates a child at +`0xA0` and sets its geometry:

- X = 35
- Y = 50
- W = 335
- H = 180

This is a hard geometry point.

The same constructor also creates four large sibling graphic layers starting at +`0x75C`, stride `0x54`.

Each layer is assigned:

- W = 480
- H = 200

Their X/Y are read from a small geometry state structure at offsets +`0x0C`/+ `0x0E`. The base constructor initializes these geometry fields to zero, and this constructor does not replace them before the first geometry application.

Initial/static conclusion:
- layer 0: X=0, Y=0, W=480, H=200
- layer 1: X=0, Y=0, W=480, H=200
- layer 2: X=0, Y=0, W=480, H=200
- layer 3: X=0, Y=0, W=480, H=200

Dynamic updates may later move these layers; this is marked OPEN until the update path is fully closed.

## 6. 47E54 — exact text widget geometry

`FUN_08047E54` creates an internal child at +`0x33C`.

Hard firmware values:
- resource/TypedText ID = `0x1D4` = 468
- X = 135
- Y = 60
- W = 200

TypedText table recovery proves ID 468 is:

`Ruch rusztu interwał [min]`

The height is derived through the generic text-resource dimension path rather than hardcoded at this callsite. Therefore:
- X/Y/W = HARD
- H = dynamic/resource-derived, OPEN for this constructor alone.

This is strong evidence that 47E54 is a parameter/configuration text component, not a generic Home icon.

## 7. 47244 — exact position, dimensions still dynamic

`FUN_08047244` creates an internal child at +`0x60`.

Hard values:
- X = 50
- Y = 55

Its width/height are not hardcoded at the same callsite; they are established through the custom widget/resource path. Therefore:
- X/Y = HARD
- W/H = OPEN.

## 8. Boiler widget 469E8 — hard internal geometry

`FUN_080469E8` is instantiated four times by `FUN_0803E34C`.

Each instance contains:

### Main internal drawing object
Object +`0x168`:
- X = 0
- Y = 0
- W = 1000
- H = 1000

This is a large internal drawing/canvas region, not necessarily a visible 1000×1000 screen area.

### Bitmap/resource child
Object +`0x13C`:
- resource ID = 14

### Text child
Object +`0x5C`:
- resource/TypedText ID = `0x1ED` = 493
- X = 0
- Y = 130
- W = 70
- H = dynamically derived.

### Another text/status child
Object +`0xCC`:
- resource/TypedText ID = `0x1ED` = 493
- X = 25
- Y = 40
- W = 45
- H = 50

These values are hard internal widget geometry. The parent-level position of each of the four 469E8 instances remains unresolved.

## 9. Hopper component: do NOT promote it to Home geometry

`FUN_0802BDF0` / `FUN_0802C294` is the component that contains the hardcoded hopper resources:

- bitmap 51
- bitmap 52
- bitmap 53

The update path `0802DA54` changes between 51/52/53.

This proves the hopper bitmap state machine.

It does NOT, by itself, prove that these three bitmaps are positioned on the visible Home screen. The component also contains many parameter/configuration TypedText resources, so it is safer to classify it as a reusable/large burner-hopper component until the parent visual path is closed.

## 10. Bitmap ID negative-evidence pass

A direct immediate scan found no hardcoded immediate loads of:
- bitmap 77
- bitmap 115
- bitmap 144
- bitmap 174

This means their presence in older Home/card work cannot be treated as direct proof of firmware geometry.

They may be:
- table-driven,
- loaded indirectly,
- resolved through a model/resource array,
- or simply belong to a different implementation.

Therefore these four IDs remain OPEN for firmware-only Home geometry.

## 11. Bitmap table hard facts

Bitmap table:
- file offset `0x54450`
- 188 entries
- stride `0x14`

Confirmed dimensions include:

| bitmap | W | H |
|---:|---:|---:|
| 51 | 34 | 29 |
| 52 | 34 | 29 |
| 53 | 34 | 29 |
| 77 | 30 | 26 |
| 91 | 39 | 23 |
| 92 | 39 | 23 |
| 115 | 40 | 41 |
| 144 | 36 | 41 |
| 151 | 31 | 30 |
| 152 | 31 | 30 |
| 174 | 40 | 38 |

The dimensions come directly from the firmware bitmap table.

## 12. Bottom/status-bar style objects discovered in the 0803E5AC update path

The update code around `080480C0` creates/positions two resource children:

### First
- parent descriptor: root + `0xA604`
- container dimensions initialized:
  - W = 480
  - H = 50
- bitmap/resource ID = 91
- child centered relative to the 480×50 container.

### Second
- parent descriptor: root + `0xA604+0x2C`
- container dimensions:
  - W = 480
  - H = 50
- bitmap/resource ID = 92
- child centered relative to its container.

These are hard geometry relationships, but their semantic role as Home top/bottom bars is NOT closed.

## 13. Coordinate-system conclusion

The firmware repeatedly uses:
- full-screen: 480×272
- large graphic canvas: 480×200
- status containers: 480×50
- central graphic region: 335×180 at (35,50)
- vertical selector: X=100, Y=50..220.

This strongly constrains the eventual 480×272 Home composition.

## 14. Current geometry confidence matrix

| component | geometry | confidence |
|---|---|---|
| 480×272 full-frame widget in 2C294 | (0,0,480,272) | HARD |
| 47290 slot 0 | (100,50) | HARD |
| 47290 slot 1 | (100,84) | HARD |
| 47290 slot 2 | (100,118) | HARD |
| 47290 slot 3 | (100,152) | HARD |
| 47290 slot 4 | (100,186) | HARD |
| 47290 slot 5 | (100,220) | HARD |
| 47604 central child | (35,50,335,180) | HARD |
| 47604 layer 0 | (0,0,480,200) initial | HARD/initial |
| 47604 layer 1 | (0,0,480,200) initial | HARD/initial |
| 47604 layer 2 | (0,0,480,200) initial | HARD/initial |
| 47604 layer 3 | (0,0,480,200) initial | HARD/initial |
| 47E54 text child | (135,60,200,H) | HARD except H |
| 47244 child | (50,55,W,H) | HARD except W/H |
| 469E8 main internal canvas | (0,0,1000,1000) | HARD internal |
| 469E8 child +0x5C | (0,130,70,H) | HARD except H |
| 469E8 child +0xCC | (25,40,45,50) | HARD |

## 15. What remains before claiming "FULL HOME GEOMETRY"

The following must be closed from firmware, not from old card projects:

1. Which factory/screen object is the actual visible Home entry point.
2. Parent-level placement of the four 469E8 boiler instances.
3. Runtime geometry updates for the 47604 four 480×200 layers.
4. Parent-level geometry of 47244.
5. Parent-level geometry of 47290.
6. Geometry of root +0xA654 / +0xA680 bitmap children after their runtime resource selection.
7. Geometry of +0xA5FC / +0xA628 and +0xA6AC..+0xA6DC helper/visual objects.
8. Touch rectangles vs visual rectangles must be separated.
9. Visibility gating must be separated from construction geometry.
10. The screen factory must be traced backward until the actual Home navigation entry is proven.

## 16. Next attack direction

Do NOT restart the analysis.

Continue from the raw firmware with these targeted passes:

A. Trace the screen factory around 0x384xx -> 0x3Axxx -> 0x3Exxx and identify which concrete class is selected for the Home route.

B. Reverse from the known Home runtime/event path into the factory, instead of forward guessing from widget constructors.

C. Trace all writes/reads of root offsets:
- 0x8F70
- 0x92DC
- 0x963C
- 0xA26C
- 0xA5FC
- 0xA628
- 0xA654
- 0xA680
- 0xA6AC
- 0xA6BC
- 0xA6CC
- 0xA6DC

D. Resolve 469E8 parent placement.

E. Resolve 47604 dynamic x/y state and all four layer update paths.

F. Resolve 47244 width/height.

G. Resolve the actual firmware use of bitmap IDs 77/115/144/174 through indirect/table-driven resource resolution.

## Evidence rule

No old-project geometry is used as proof here. When a semantic label is not directly supported by the firmware path, it is marked OPEN.
