# MULTIPASS — 2261..2265 ARE GRAPH BARS/POINTS, NOT 47290 VERTICAL LIST — 2026-11-20

## User correction
The user correctly points out that 0x2261..0x2265 are not displayed as a vertical list. On the actual controller they form the fan-modulation curve: five adjacent vertical bars/columns, one for each boiler-power point 20/40/60/80/100%, with the value determining bar height/point position.

## PASS 1 — independent semantic confirmation
The repository's own point table defines:
- 0x2261 = blower speed at boiler power 20%
- 0x2262 = blower speed at 40%
- 0x2263 = blower speed at 60%
- 0x2264 = blower speed at 80%
- 0x2265 = blower speed at 100%

All are U16, range 0..100.

## PASS 2 — independent firmware/card bitmap confirmation
Firmware bitmap pair:
- 056 = 20x20 graph point normal
- 057 = 20x20 graph point selected

Existing direct-BIN visual audit identifies 056/057 specifically as the five-point fan-modulation graph markers.

Thus the visual representation is a graph/column family, not a six-row vertical selector.

## PASS 3 — critical correction to earlier inference
The fact that FUN_0803EC18 resolves panel indices 74..83 DOES NOT prove that FUN_08047290 displays indices 74..79.

The call to FUN_080484B0 / FUN_08047334 is only one branch inside a broader update/orchestration function. The same 0803EC18 path resolves multiple model values and updates multiple sibling UI components.

Therefore the earlier statement 'first six 3EC18 IDs correlate with 47290 labels' is withdrawn as an architectural inference.

What is hard:
- 3EC18 fetches panel IDs 0x4A..0x53 through FUN_08036FF2.
- 74..79 correlate semantically to 2252/2261..2265.
- 47290 is a separate six-slot component using its own runtime +0x08 TypedText-ID array.
What is NOT hard:
- that 47290 labels are 2252/2261..2265.

## PASS 4 — graph vs list asset separation
- 056/057 = graph points.
- 151/152 = 47290 vertical-selector state pair.
They are visually similar but belong to different components.

47290 geometry is Y=50,84,118,152,186,220, i.e. six vertically stacked slots. This geometry is incompatible with the user's observed five adjacent graph columns.

## PASS 5 — page architecture
FUN_0802EADE is a host/content switching primitive:
- 08048468 -> host +0x84F4, content
- 080484B0 -> host +0x84F4, content
- 080484F0 -> host +0x84F4, content
- 08048520 -> host +0x84F4, another content

This strongly supports a reusable host/content architecture. 0803EC18 is therefore better modeled as a page/model refresh dispatcher than as the constructor of one literal visual arrangement.

## PASS 6 — likely graph mechanism
The most likely chain is:
0x2261..0x2265 values
 -> model resolver FUN_08036FF2
 -> graph widget/update sibling
 -> five X positions with value-derived Y/bar heights
 -> 056/057 markers

This is a hypothesis until the exact graph renderer and its writer are traced.

## PASS 7 — implications for hidden layers
The firmware can contain persistent components and hidden/inactive content, but the evidence does not support 'all menu screens are fully rendered simultaneously'. Host/content switching is concrete evidence for dynamically selected content.

## PASS 8 — what to attack next
1. Find every raw/indirect use of bitmap 056 and 057 and cluster by parent.
2. Trace which widget receives values resolved from panel indices 75..79.
3. Find geometry writer for those five graph points/bars.
4. Separately trace 47290's six TypedText IDs from its +0x08 source.
5. Compare update timing/parents: graph branch vs 47290 branch.
6. Close indices 80..83.
7. Only then decide whether 3EC18 is the refresh function of the modulation page, a shared model page, or a broader controller.

## Confidence
- 2261..2265 = five fan-modulation points: HARD.
- 056/057 = graph point markers: HARD.
- 47290 = vertical six-slot component: HARD.
- 47290 = 2261..2265 list: REJECTED / withdrawn.
- host/content switching: STRONG/HARD from caller structure.
