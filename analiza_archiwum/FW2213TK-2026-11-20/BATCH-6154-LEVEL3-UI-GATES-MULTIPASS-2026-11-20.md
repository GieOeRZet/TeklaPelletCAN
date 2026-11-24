# TeklaPelletCAN — PIN 6154 / ACCESS LEVEL 3 — UI GATES MULTIPASS
Date: 2026-11-20
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## EXECUTIVE RESULT

User asked what PIN "6164" does. Firmware proof shows the fixed code is 6154, not 6164.

6154 decimal = 0x180A and FUN_08037E74 maps it to access level 3.

The key new result is that level 3 is not merely a menu visibility tier.

There are 17 distinct UI constructor/setup paths containing a direct hard gate:

model/context + 0x158 >= 3
    -> add child object at parent + 0x23C

The child at +0x23C belongs to a common numeric-editor/control class.

A common event handler at FUN_0802FB04 proves that when the event target is parent+0x23C it increments the editor's value at parent+0x60, bounded by parent+0x64. The sibling target parent+0x284 decrements the value.

Therefore the strongest current interpretation is:

6154 unlocks an additional '+' / increment control in a family of parameter editors/screens.

The exact human-readable labels/screens corresponding to all 17 paths are not yet closed. Do not invent names.

## PASS 01 — CODE CORRECTION

The user wrote 6164.
Raw firmware contains movw r2,#0x180A.
0x180A decimal = 6154.

Mapping:
- 900 -> level 1
- 999 -> level 2
- 6154 -> level 3

No equivalent fixed 6164 was found in the access-level resolver.
[FW][CLOSED]

## PASS 02 — ACCESS LEVEL STORAGE

FUN_08037E74 writes the resolved level to context/model + 0x158.
Values are 0,1,2,3.
FUN_0803C21C subsequently reads +0x158 and derives a separate has-access boolean.
[FW][CLOSED]

## PASS 03 — EXACT LEVEL-3 GATE

Representative path at 0x4A566:

LDRB r0,[r0,#0x158]
CMP r0,#3
BLT skip
...
ADD r1,parent,#0x23C
ADD r0,parent,#4
BL 0x30380

Thus +0x23C is added to the screen/container only when access level >=3.
This is a hard visibility/tree-construction gate.
[FW][CLOSED]

## PASS 04 — 17 DISTINCT LEVEL-3 GATES

Verified direct occurrences:
- 0x4A566
- 0x4AA42
- 0x4B22A
- 0x4C15A
- 0x4EA32
- 0x4F456
- 0x4F79A
- 0x4FEF2
- 0x501F2
- 0x504AE
- 0x5076A
- 0x50A7E
- 0x50D3A
- 0x50FF6
- 0x512B2
- 0x5156E
- 0x5FB0A

These are separate constructor/setup paths, not repeated instructions in one function.
[FW][CLOSED]

## PASS 05 — +0x23C IS A REAL UI CONTROL

The +0x23C object is initialized through FUN_0802FC10, which creates the relevant widget object.
The screen setup configures its resource and geometry and, only for access>=3, adds it to the child tree.
This proves it is not merely a flag or hidden data structure.
[FW][CLOSED]

## PASS 06 — EVENT HANDLER PROVES '+' SEMANTICS

FUN_0802FB04 receives an event target in r1.
At 0x2FB38 it compares the target with parent + 0x23C.
If equal:

value = parent + 0x60
limit = parent + 0x64
if value < limit:
    value++

The new value is written back to +0x60 and refreshed/propagated.
[FW][CLOSED]

## PASS 07 — SIBLING MINUS CONTROL

The same FUN_0802FB04 checks parent + 0x284.
If that is the event target:

value = parent + 0x60
if value >= 1:
    value--

So the same widget family has:
- +0x23C = increment / '+'
- +0x284 = decrement / '-'
[FW][CLOSED]

## PASS 08 — WHY THIS MATTERS

6154 therefore changes the interaction model, not only menu visibility.
For the affected screens, access<3 means the + control is not attached to the screen tree; access>=3 means it is attached.
The common handler still knows about both + and - targets.
This is consistent with a service/installer-level editing privilege, but the exact parameter semantics differ per screen and are not yet closed.
[FW][STRONG]

## PASS 09 — 0900 / 0999 COMPARISON

The 0..3 access resolver is cumulative: 0900->1, 0999->2, 6154->3.
The direct level-3 UI gates test level<3, so neither level 1 nor level 2 gets these specific +0x23C controls.
[FW][CLOSED]

## PASS 10 — IMPORTANT DISTINCTION FROM MAIN MENU

The earlier 21-row menu constructor uses access_level != 0 for its second-stage rows.
Therefore 6154 does NOT uniquely create all six second-stage rows. 0900 already enables that branch.
6154's unique effect is the explicit >=3 gates identified in this batch.
[FW][CLOSED]

## PASS 11 — SCREEN LABELS ARE NOT YET SAFE TO NAME

The 17 paths are clearly UI constructors/setup functions, but the current evidence does not yet prove the human-readable screen names for every one.
The +0x23C control is configured with resource ID 0x1C6 in representative constructors, but resource-ID-to-human-label mapping is not yet closed.
Therefore do not call these service menu, installer menu, diagnostics, or factory settings without independent proof.
[OPEN]

## PASS 12 — CURRENT HARD CONTRACT

6154 definitely:
1. sets access level = 3;
2. preserves the cumulative access model;
3. unlocks all UI paths gated by access >= 3;
4. adds a +0x23C increment control in 17 distinct screen/setup paths;
5. that control increments the current editor value (+0x60) up to its limit (+0x64);
6. the sibling +0x284 control decrements the same value.

## NEXT ATTACK

For each of the 17 paths trace: parent class/vtable, parameter binding, +0x60 source, +0x64 limit, +0x23C resource 0x1C6, title/TypedText resource, touch callback/navigation, and underlying parameter/CAN ID.

Target output:
6154 -> level 3 -> screen A/B/... -> exact parameter/function unlocked.

## CONTRADICTION / STALE-HYPOTHESIS CHECK

Withdraw:
- "6164 is the code" -> corrected to 6154.
- "6154 simply opens a service menu" -> unproven.
- "level 3 is only a visibility flag" -> false; it directly changes widget-tree construction and interaction.
- "the six second-stage main-menu rows are level-3 only" -> false; they require any nonzero access.

Current strongest statement:
6154 = access level 3, with explicit >=3 UI gates that add an increment control to 17 parameter-editor/setup paths.