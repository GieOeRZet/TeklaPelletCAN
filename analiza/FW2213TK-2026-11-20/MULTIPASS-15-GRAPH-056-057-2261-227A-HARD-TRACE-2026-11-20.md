# MULTIPASS-15 — GRAPH 056/057 + 0x2261..0x227A HARD TRACE — 2026-11-20

## Scope
Independent raw-BIN multi-pass on `FW2213TK_kopia.bin` (SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`).
Focus:
1. bitmap 056/057 call-sites;
2. graph constructor/update chain;
3. exact parameter-to-point binding;
4. indices 80..83;
5. graph host/content boundary;
6. separation from FUN_08047290 / 151/152.

## PASS A — direct raw code trace: graph object

### A1. FUN_08048520 is the graph-component constructor/update entry
Raw address `0x48520`.

Hard caller:
- `0x3ED26 -> 0x48520`.

At `0x3ED26` the caller prepares:
- R0 = `*(R8 + 0x8) + 0x14`-derived object/component pointer (exact parent chain retained in raw trace);
- R1 = `SP+0x8`, an array of five 8-byte point records;
- R2 = 5;
- R3 = 0;
- stack arg0 = 100;
- stack arg1 = 126.

The point array is initialized at:
- +0x00: 20
- +0x08: 40
- +0x10: 60
- +0x18: 80
- +0x20: 100

and the corresponding second word of each 8-byte point is populated from resolver results:
- point 0 second word = resolver index 0x4A
- point 1 second word = 0x4B
- point 2 second word = 0x4C
- point 3 second word = 0x4D
- point 4 second word = 0x4E

Thus the graph is built from five explicit X positions (20/40/60/80/100) plus five runtime Y values.

### A2. 0x4A..0x4E -> exact parameter IDs
Inside `FUN_0803EC18` raw `0x3EC18`:
- `0x4A -> FUN_08036FF2(context,0x4A)`
- `0x4B -> ...`
- `0x4C -> ...`
- `0x4D -> ...`
- `0x4E -> ...`

The raw mapping table at `0x3765E` independently contains:
- 0x4A -> 0x2261
- 0x4B -> 0x2262
- 0x4C -> 0x2263
- 0x4D -> 0x2264
- 0x4E -> 0x2265

Therefore the graph point binding is HARD:

| Point | X | panel index | parameter |
|---|---:|---:|---:|
| 1 | 20 | 0x4A | 0x2261 |
| 2 | 40 | 0x4B | 0x2262 |
| 3 | 60 | 0x4C | 0x2263 |
| 4 | 80 | 0x4D | 0x2264 |
| 5 | 100 | 0x4E | 0x2265 |

No inference from screenshot is needed for this mapping.

### A3. Exact parameter semantics
The repository's register catalogue independently identifies:
- 0x2261 = blower curve point at boiler power 20%
- 0x2262 = blower curve point at boiler power 40%
- 0x2263 = blower curve point at boiler power 60%
- 0x2264 = blower curve point at boiler power 80%
- 0x2265 = blower curve point at boiler power 100%

Therefore the firmware code directly confirms the observed five-point blower modulation graph.

## PASS B — graph geometry engine

### B1. FUN_08047A8A consumes exactly five point records
Raw `0x47A8A`:
- R2 is count;
- the caller passes count = 5;
- the input records are 8 bytes apart;
- the function calls `FUN_08047C1A` once per point;
- remaining point slots are cleared after the active count.

This is not a generic six-row selector.

### B2. FUN_08047C1A is the point geometry/value writer
Raw `0x47C1A`:
- clamps Y against object min/max;
- clamps X against object min/max;
- stores the point values in per-point storage;
- computes a vertical pixel coordinate using a 300-pixel scale;
- computes horizontal position from the X range;
- addresses each point graphics object using a 0xE4 stride;
- point graphic composite is reached at point-base + 0x2E8;
- a further +0x708 object is updated for the zero/nonzero point cases;
- sibling graphic region uses +0x75C stride.

The important hard structural facts are:
- 5 point records;
- point stride = 0xE4;
- each point has its own graphic subtree;
- Y uses a 300-unit interpolation;
- the point graphics are not the 47290 six-slot widgets.

### B3. Bitmap 056 is hard-linked to the graph point updater
At raw `0x47DAE`:
- `MOVS R0,#0x38` = decimal 56
- value is passed through stack to `FUN_080307BC`
- target child is point-local `+0x2C` after point/object arithmetic.

Therefore:
`graph point -> Bitmap resource 056` is HARD.

This is much stronger than a bitmap-atlas visual guess.

## PASS C — bitmap 057

A complete direct-call scan for `FUN_080307BC` with literal resource 57 found two raw call-sites:
- `0x47558`
- `0x475C2`

Both belong to the `0x4752C/0x475A4` family, not to `FUN_08047A8A/FUN_08047C1A/FUN_08047D80`.

Therefore:
- 056 is hard-closed as graph point resource;
- 057 remains visually identified as the selected graph-point pair;
- however, this pass does NOT prove that the 057 writer is the same graph object path.

This distinction is intentional. Do not collapse 057 into 056's call-site without another xref.

## PASS D — 0x4F..0x53 and indices 80..83

The alternate branch in `FUN_0803EC18` resolves:
- 0x4F
- 0x50
- 0x51
- 0x52
- 0x53

The same raw mapping table at `0x3765E` gives:
- 0x4F -> 0x2268
- 0x50 -> 0x226E
- 0x51 -> 0x226F
- 0x52 -> 0x2275
- 0x53 -> 0x227A

Repository register catalogue identifies these as the five exhaust-fan characteristic values:
- 0x2268 = exhaust fan curve 1
- 0x226E = exhaust fan curve 2
- 0x226F = exhaust fan curve 3
- 0x2275 = exhaust fan curve 4
- 0x227A = exhaust fan curve 5

Therefore indices 80..83 are NOT missing:
- 80 = 0x2268
- 81 = 0x226E
- 82 = 0x226F
- 83 = 0x2275
and the fifth member is index 87 = 0x227A in the repository's panel index catalogue.

Important: the firmware's `0x4F..0x53` sequence is five exhaust-curve values; the external catalogue numbering for 0x227A is not contiguous with 80..83. Do not manufacture a contiguous panel-index sequence.

## PASS E — graph vs exhaust curve

The raw code strongly indicates `FUN_0803EC18` is a shared refresh/dispatch routine with two branches:
- one branch for parameter family 0x2261..0x2265 (blower modulation graph);
- one branch for parameter family 0x2268/0x226E/0x226F/0x2275/0x227A (exhaust fan curve family).

Thus 0x4A..0x53 are not ten labels of one visual vertical list.
They are resolver indices feeding model/UI update paths.

## PASS F — graph host/content architecture

`FUN_08048520` stores/builds its graph component at:
- parent + `0x963C`.

It then calls:
- `FUN_0802EADE(parent + 0x84F4, graph_component)`.

Therefore the graph is inserted into the established dynamic host/content mechanism:
- host = parent + 0x84F4
- graph content = parent + 0x963C

This is strong firmware evidence that the graph is a content page/component, not a permanent Home six-slot widget.

## PASS G — separation from FUN_08047290

`FUN_08047290` remains the separate six-slot component at parent +0x92DC.
Its geometry/resource family is independent:
- six slots;
- vertical Y sequence;
- 151/152 state pair;
- separate update/constructor path.

The current graph trace does not call `FUN_08047290`.
Therefore:
- 056/057 graph != 151/152 selector;
- graph point count 5 != 47290 slot count 6.

## PASS H — 47290 is not the blower graph

The graph path now has an independent hard chain:

`FUN_0803EC18`
-> panel index 0x4A..0x4E
-> parameter IDs 0x2261..0x2265
-> five (X,Y) point records
-> `FUN_08048520`
-> `FUN_08047A8A`
-> `FUN_08047C1A`
-> point graphic subtree
-> Bitmap resource 056.

This is sufficient to reject any interpretation that required 47290 to display 0x2261..0x2265.

## PASS I — observed screenshot correlation

The user-observed screen has five adjacent vertical bars/curve points for blower modulation.
The firmware now independently produces:
- five points;
- X = 20/40/60/80/100;
- Y = 0x2261..0x2265;
- graph-specific point geometry;
- graph-specific Bitmap 056.

This is a direct firmware-to-screen correlation, not a guess based on names.

## Remaining OPEN items
1. Exact 057 selected-state writer in the graph path.
2. Exact graph viewport X/Y/W/H in final screen coordinates (the point geometry formulas are partially closed, but final parent placement still needs one more pass).
3. Which screen/page ID selects the `parent+0x963C` graph content.
4. Whether the alternate 0x4F..0x53 exhaust curve is rendered by the same graph class or another graph/content branch.
5. Exact semantics of the stack args 100 and 126 in `FUN_08048520 -> FUN_08047A8A`.
6. Exact x/y axis labels and text resources for the graph page.
7. Whether 057 is selected state via a separate reusable point-control class.

## Confidence
- 0x2261..0x2265 -> five graph points: HARD.
- X positions 20/40/60/80/100: HARD.
- 056 -> graph point resource: HARD.
- graph component at parent +0x963C: HARD.
- graph uses dynamic host +0x84F4: HARD.
- 47290 != graph: HARD.
- 0x4F..0x53 -> exhaust curve family: HARD.
- 057 -> graph selected state: STRONG visual/resource evidence, but direct writer still OPEN.

## Important address convention
This pass uses the established raw firmware mapping:
- raw offset 0x3EC18 -> runtime 0x0803EC18;
- raw offset 0x47A8A -> runtime 0x08047A8A;
- raw offset 0x47C1A -> runtime 0x08047C1A;
- raw offset 0x47DAE -> runtime 0x08047DAE.

Do not apply the earlier discarded +0x10000 correction to these raw/runtime addresses.
