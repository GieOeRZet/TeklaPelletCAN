# MULTIPASS-16 — REUSE OF GRAPH MARKERS / CONFIGURATION UI CORRELATION — 2026-11-20

## User hypothesis under test
Hypothesis: graphics visually similar to the modulation-curve markers are reused in configuration/setup screens (e.g. heating setup, room controller/source selections), rather than being unique to the modulation curve.

## Hard findings from raw firmware

### 1. 056 is definitely used by the graph-point update path
`FUN_08047D80` contains:
- loop over active graph points;
- `MOVS R0,#0x38` = bitmap resource 056;
- `FUN_080307BC` on point child +0x2C;
- point objects are addressed with stride 0xE4;
- graph has up to 5 points.

This is direct firmware proof that bitmap 056 belongs to the graph point rendering/update family.

### 2. 057 is a genuine selected-state asset, but its firmware reuse is broader than the graph
The extracted bitmap is 20x20 and visually is the green/cyan selected counterpart of 056.
The web/card implementation independently maps:
- fmp -> U(56)
- fmp.sel -> U(57)

Therefore the pair is semantically a reusable point/selection marker.

However, the raw firmware direct-literal scan gives an important nuance:
- direct literal resource 056 writer: graph path at 0x47DAE;
- direct literal resource 057 writers: 0x47558 and 0x475C2 inside FUN_0804752C / FUN_080475A4.

Those 057 functions are NOT direct callers of the graph's FUN_08047A8A/FUN_08047C1A path.

Therefore we must NOT say '057 is only the graph selected point'. The stronger and safer interpretation is:
**056/057 are a reusable visual state pair; 056 is hard-proven in the graph point path, while 057 has an additional firmware consumer outside that direct graph path.**

### 3. 057 has a separate UI consumer near the six-slot/content component region
FUN_0804752C:
- operates on its own object;
- writes bitmap 057 through FUN_080307BC;
- performs geometry calculation before/after the bitmap update;
- has a second sibling method FUN_080475A4 that also writes bitmap 057.

The surrounding firmware region contains:
- FUN_08047290 = six-slot component;
- FUN_08047334 = six-slot label/slot builder;
- FUN_0804752C / FUN_080475A4;
- FUN_08047604 = separate graph component constructor.

Thus 057 is demonstrably reused in UI code outside the graph constructor/update entry.

### 4. Critical namespace warning
TypedText ID 57 = 'Ogrzewanie 1'.
Bitmap resource 57 is a separate numeric namespace.
The coincidence of number 57 is NOT evidence that bitmap 057 is an 'Ogrzewanie 1' icon.

### 5. Graph itself is a configuration/service-page component
The graph constructor:
- FUN_08047604
- creates five point objects at parent +0x2E8 with stride 0xE4;
- creates four large graphic regions at +0x75C with stride 0x54;
- establishes central graphic region at X=35,Y=50,W=335,H=180;
- FUN_08048520 places the graph content at parent +0x963C;
- FUN_08048520 inserts that content into host parent +0x84F4.

The graph therefore belongs to a dynamic content page, not Home.

### 6. The same graph class is fed by two parameter families
FUN_0803EC18 prepares the same five-point structure for:
- 0x2261..0x2265 = blower curve 20/40/60/80/100%;
and a second branch:
- 0x2268, 0x226E, 0x226F, 0x2275, 0x227A = exhaust/assist-fan curve family.

Both branches pass five X positions:
20, 40, 60, 80, 100
into FUN_08048520.

This is hard evidence that the point/curve rendering mechanism is intentionally reusable across different configuration curves.

## External/project correlation, clearly marked as non-firmware-only
The project web implementation uses the same 056/057 pair for its generic `.fmp/.fmp.sel` point controls.
The web UI also places 'Moc dmuchawy modulacja [%]' under burner settings/service level.

This supports the reusable-widget interpretation, but firmware evidence remains primary.

## Conclusion
The user's hypothesis is directionally correct, with an important refinement:

**The curve marker graphics should be treated as a reusable UI primitive, not as graphics unique to one curve.**

What is hard-proven:
- 056 = graph normal point resource;
- 057 = selected counterpart asset;
- 057 has at least one additional firmware consumer outside the direct graph updater;
- the graph component itself is reusable for multiple parameter families.

What is NOT yet proven:
- exact configuration screen represented by the 057 consumer at 4752C/475A4;
- whether that consumer is specifically 'room controller', 'source', or another heating-selection control;
- exact parent/content/page ID of that consumer.

## Next attack
1. Recover the caller/vtable origin of FUN_0804752C and FUN_080475A4.
2. Identify their parent object and child hierarchy.
3. Recover exact X/Y/W/H of the 057 consumer.
4. Trace adjacent bitmap resources in that same object.
5. Compare its geometry/resource family with heating/source/room-controller configuration screens.
6. Scan all reusable circular/selector bitmap pairs (not only 056/057) and cluster them by firmware object/class.
7. Build a resource-reuse matrix: bitmap pair -> constructor/class -> screen/content -> parameter family.

This should test the user's hypothesis without assuming it.
