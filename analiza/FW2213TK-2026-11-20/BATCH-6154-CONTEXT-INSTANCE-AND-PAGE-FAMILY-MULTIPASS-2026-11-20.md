# BATCH — 6154 / CONTEXT / INSTANCE / PAGE-FAMILY MULTIPASS — 2026-11-20

## Purpose

Continuation of the 6154 level-3 audit. This batch deliberately does NOT assume that offsets 0x12A/0x12B/0x12C are parent fields or that 0x3D8 is already a proven model binding. The firmware was re-traced from raw disassembly with multiple independent passes.

Evidence tags:
- [FW] direct raw firmware/disassembly
- [STRONG] converging independent traces
- [OPEN] unresolved

---

## PASS 1 — Re-audit of 6154 gates

The previously closed result survives:

17 wrapper/setup paths:
4A510, 4A9EC, 4B1D4, 4C104, 4E9DC, 4F400, 4F744, 4FE9C, 5019C, 50458, 50714, 50A28, 50CE4, 50FA0, 5125C, 51518, 5FAB4.

All use the same access-byte gate:
context + 0x158 >= 3.

All add parent + 0x23C only after the gate and then continue with the common widget tree.

[FW] 6154 therefore changes actual widget-tree membership, not merely menu visibility.

---

## PASS 2 — 0x23C / 0x284 interaction semantics

[FW] FUN_0802FB04:
- +0x23C = increment control.
- +0x284 = decrement control.
- increment: +0x60 is incremented while +0x60 < +0x64.
- decrement: +0x60 is decremented while +0x60 >= 1.

Therefore:
- +0x60 = current numeric selection/value/index for this widget family.
- +0x64 = upper bound for the same family.

Exact semantic unit (CO index, menu item index, parameter value, etc.) remains [OPEN] per parent.

---

## PASS 3 — CRITICAL CORRECTION: 0x12A IS NOT THE PARENT FIELD

The earlier interpretation was too loose.

[FW] Example parent constructor:
0x080405B6:
  BL 0x080314BA
  MOVS r1,#2
  STRB r1,[r0,#0x12A]

FUN_080314BA returns a pointer loaded from SRAM global state (literal points to 0x20024814).

The same pattern occurs in multiple page constructors.

Therefore:
[STRONG] 0x12A is a byte in the global application/UI context returned by FUN_080314BA, not a field of the page object itself.

Observed writes immediately before level-3 wrapper invocation:
- 0x080405C4 -> global/context +0x12A = 2 -> wrapper 0x0804A510
- 0x08040C5A -> +0x12A = 2 -> wrapper 0x0804A9EC
- 0x080411A8 -> +0x12A = 4 -> wrapper 0x0804B1D4
- 0x0804B348 -> +0x12A = 5 -> wrapper 0x0804F400
- 0x0804B622 -> +0x12A = 2 -> wrapper 0x0804F744
- 0x0805F466 -> +0x12A = 2 -> wrapper 0x0805FAB4

Human meaning of 2/4/5 is [OPEN]. Do not call these values menu numbers without tracing the dispatcher.

---

## PASS 4 — 0x12C IS A REAL INSTANCE SELECTOR

A full xref search found several direct writes to global/context +0x12C.

[FW] FUN_08037D00 / related selector path:
- values 1,2,3,4 are selected by a table/switch.
- selected value is written to context +0x12C.
- later code uses this state while resolving installation/instance data.

[FW] 0x08040FDC:
- iterates a table;
- for every entry whose byte is not 0xFF:
  BL 0x080314BA
  STRB table_byte,[context,#0x12C]

[FW] 0x0804103E does the same for another indexed table.

[STRONG] +0x12C is an active instance selector with valid values 1..4 in this path. This is consistent with CO1..CO4 instance selection.

This is independent of +0x12A.

---

## PASS 5 — 0x12B IS A DIFFERENT CONTEXT SELECTOR

A complete direct-store search for byte writes to context +0x12B found only one code location:

0x08038568:
  MOVS r1,#0x10
  STRB r1,[r0,#0x12B]

and its adjacent path 0x0803856C writes 0x11.

The caller/dispatcher is around 0x0803C064..0x0803C176, which is a selector dispatch over a table of cases.

[STRONG] +0x12B is NOT the same thing as +0x12C.

Its exact human meaning is [OPEN].

---

## PASS 6 — 0x12B controls a repeated page family

Three large constructors contain the same pattern:

- 0x0804D00C
- 0x0804D634
- 0x0804D948

Each:
1. calls FUN_080314BA
2. writes global +0x12A = 2
3. calls a local setup helper
4. reads global +0x12B
5. switch range 0..10
6. selects a bitmap/resource ID
7. constructs the page

Resource selection table in all three:

selector 0 -> 0x29
selector 1 -> 0x28
selector 2 -> 0x2A
selector 3 -> 0x2B
selector 4 -> 0x2C
selector 5 -> 0x2D
selector 6 -> 0x2E
selector 7 -> 0x31
selector 8 -> 0x2F
selector 9 -> 0x30
selector 10 -> 0x29

[FW] This is a real firmware page-family selector.

Important anomaly:
the direct write search only found +0x12B values 0x10/0x11. Therefore the relationship between the 0..10 switch and the 0x10/0x11 setter path must still be resolved. Possible explanations include a transformed/indirect value, alternate initialization path, or a different lifecycle stage.

Do NOT collapse these into a guessed "CO number" mapping yet.

---

## PASS 7 — 0x12B / 0x12C separation is architecturally important

The firmware has at least three distinct context dimensions:

+0x12A = page/UI context selector [STRONG]
+0x12B = secondary class/family selector [STRONG, human meaning OPEN]
+0x12C = active instance selector 1..4 [STRONG]

This is highly relevant to the final resolver architecture.

The ESP implementation should model these as separate context dimensions, not as one "menu index".

---

## PASS 8 — Concrete page resource observations

Selected constructors were inspected around their first Bitmap resource setup:

- 0x080405B6 uses resource 0x33.
  Bitmap ID 0x33 = inventory bitmap 051, the empty/low hopper outline.
  [STRONG] This page is part of the fuel/hopper UI family.

- 0x08040C4E uses resource 0x36.
  Bitmap ID 0x36 = inventory bitmap 054, the large red fuel-container/tank graphic.
  [STRONG] This page is part of the fuel-storage/tank UI family.

- 0x0804B348 uses resource 0x29 (bitmap ID 41) in its main visual setup.
  Exact page semantics [OPEN].

- 0x0804B622 uses resource 0x39 (bitmap ID 57).
  Exact page semantics [OPEN].

- 0x0805F466 uses resource 0x34 (bitmap ID 52), the filled hopper/pellet-dot graphic.
  [STRONG] This is also a fuel/hopper page family.

This gives a direct route to assigning the 17 level-3 pages: resource/title/callback/config must be resolved together.

---

## PASS 9 — Rejection of an unsafe shortcut

The following is NOT proven:

"6154 means installer/service menu."

What is proven:
- access byte >=3
- extra + control inserted
- extra interaction path becomes physically present

The human name of the page must come from title/string/resource/callback tracing.

---

## PASS 10 — 0x3D8 callback remains the correct next binding target

FUN_0802FB04 reads:
  parent +0x3D8
then dereferences:
  object->vtable +0x08
and elsewhere:
  object->vtable +0x0C

[FW] This is a genuine virtual-object callback path.

However:
- no direct STR to [parent,#0x3D8] was found by the simple full-disassembly immediate-offset scan;
- therefore assignment may happen in a base/common constructor, through a copied structure, or through an indirect initialization path.

[OPEN] exact class and assignment site.

Do not yet label it "CAN write callback" as fact.

---

## PASS 11 — 0x60 / 0x64 cannot be globally renamed yet

The firmware contains many unrelated objects using offsets 0x60/0x64.

Therefore the closed statement is only:

For the numeric control object handled by FUN_0802FB04:
- +0x60 = current value/index
- +0x64 = upper bound

[OPEN] exact initialization per each of the 17 parent pages.

The next analysis must taint each parent's specific numeric-control object rather than grep globally.

---

## PASS 12 — Configuration resolver cross-check

FUN_0803C178 remains the authoritative UI configuration selector:

selector 5 -> internal 0x10F -> Hot water configuration
selector 6 -> internal 0x110 -> Solar configuration
selector 7 -> internal 0x111 -> Buffer configuration
selectors 1..4 -> internal 0x10E -> Heating/CO configuration
selector 8 -> internal 0x11C

[FW] This is independent of +0x12C active-instance state.

Therefore final page visibility must be represented as a composition of:
- page context
- active instance
- installation configuration
- access level

not as a static page list.

---

## PASS 13 — Architecture consequence

The correct final dispatcher shape is now even clearer:

installation/configuration resolver
 -> capability resolver
 -> access-level resolver
 -> page-family/context resolver (+12A/+12B)
 -> active-instance resolver (+12C)
 -> page constructor/widget tree
 -> numeric-control state (+60/+64)
 -> callback/model binding (+3D8)
 -> record/CAN side effects

The renderer must not implement any of these policy decisions.

---

## PASS 14 — Synthetic matrix implications

At minimum, the future reconstruction tests must exercise:

A. CO1 only
B. CO1 + CWU
C. CO1 + CO2 + CWU
D. CO1 + CO2 + CWU + Buffer
E. CO1..CO4 + CWU
F. CO1..CO4 + CWU + Buffer + Solar
G. F + Additional fuel storage
H. G + Cascade master
I. module/profile variants
J. access 0
K. access 1
L. access 2
M. access 3

For each, compare:
- page existence
- widget-tree delta
- +0x12A/+0x12B context
- +0x12C active instance
- numeric range
- touch controls
- callback binding
- configuration gates

---

## PASS 15 — Stale-hypothesis audit

Withdraw/avoid:
- +0x12A = parent field
- +0x12B = active instance
- +0x12C = generic menu number
- 6154 = simply "service menu"
- 0x3D8 = proven CAN writer
- 0x35786 = proven CAN/record write
- repeated 0x29/0x28.. resources = proven CO1..CO4 mapping

These are either corrected or still [OPEN].

---

## Next exact targets

1. Recover the complete 0x3D8 assignment path.
2. Identify vtable +0x08/+0x0C implementation targets.
3. Trace parent+0x140 numeric widget to the model/record object.
4. For all 17 callers, recover exact +0x60/+0x64 initialization.
5. Resolve page titles/resources for all 17.
6. Resolve +0x12A values to actual dispatcher/page families.
7. Resolve +0x12B 0x10/0x11 path and the 0..10 resource switch.
8. Cross each page against 0x10E/0x10F/0x110/0x111 and module/profile/cascade/storage gates.
9. Build a page-family x active-instance x configuration x access matrix.

## Bottom line

The firmware is exposing a multi-dimensional UI state machine. 6154 is one dimension (interaction permission), +0x12C is another (active instance), +0x12A/+0x12B are page/context dimensions, and configuration resolver gates are yet another dimension.

That is exactly why the final ESP implementation must be a resolver-driven reconstruction rather than a copied/static menu.


---

## PASS 16 — COMPLETE +0x12A VALUE INVENTORY

A full immediate-store inventory found context +0x12A assignments with values:
- 0
- 1
- 2
- 3
- 4
- 5

Representative sites:
- 0x08031CC4 -> 0
- 0x0803C05C -> 1
- 0x0803C5C2 -> 2
- 0x0804216C -> 1
- 0x0804804C -> 3
- 0x080411A8 -> 4
- 0x0804B348 -> 5
- many later page constructors -> 2

[STRONG] +0x12A is a compact page-family/context selector with at least six distinct states, not a simple access level and not the active CO instance.

This gives a new concrete resolver dimension.

---

## PASS 17 — CONTEXT 3 HAS EXPLICIT +0x12B VARIANT MAPPING

Constructor around 0x08048040:

1. calls FUN_080314BA -> global context
2. sets context +0x12A = 3
3. reads context +0x12B
4. chooses the page bitmap resource:

+0x12B == 0x10 -> resource 0x35
+0x12B == 0x11 -> resource 0x37
otherwise -> resource 0x32

[FW]

Resource meanings from the closed bitmap inventory:
- 0x32 = bitmap 050 (57x43)
- 0x35 = bitmap 053 (34x29, orange/yellow E-style reserve/warning)
- 0x37 = bitmap 055 (35x37)

[STRONG] +0x12B is therefore a real page/variant selector used to alter visual composition within context 3.

Its human semantic name remains [OPEN].

---

## PASS 18 — CONTEXT 2 ALSO USES +0x12B FOR A 0..10 RESOURCE FAMILY

Constructor 0x080424EC:
- sets +0x12A = 2
- reads +0x12B
- switch 0..10
- selects:
  0 -> 0x29
  1 -> 0x28
  2 -> 0x2A
  3 -> 0x2B
  4 -> 0x2C
  5 -> 0x2D
  6 -> 0x2E
  7 -> 0x31
  8 -> 0x2F
  9 -> 0x30
  10 -> 0x29

The same table exists in:
- 0x0804D00C
- 0x0804D634
- 0x0804D948

and related constructors:
- 0x0804A2EA
- 0x0805FA52

[STRONG] these are a repeated resource-family dispatch keyed by the same context byte.

Do not yet translate the 0..10 values into human labels.

---

## PASS 19 — CONTEXT 1 HAS A DISTINCT RESOURCE FAMILY

Constructor 0x08042160:
- sets +0x12A = 1
- first bitmap resource = 0x27
- bitmap 0x27 = inventory bitmap 039, 30x18 + A8

The same firmware region contains the page/resource machinery around this constructor.

[STRONG] context 1 is not merely a numeric duplicate of context 2; it has its own visual/resource family.

User's earlier interpretation that bitmap 039 may be a second fuel-storage menu tile remains [USER]/[OPEN], but the firmware proves that resource 039 belongs to a context-1 constructor.

---

## PASS 20 — CONTEXT 3 / +0x12B IS NOT ACTIVE CO INSTANCE

Independent cross-check:
- +0x12C has direct writes of values 1..4.
- +0x12B has a separate write path producing 0x10/0x11.
- context 3 uses +0x12B to choose resources 0x35/0x37/0x32.

[STRONG] +0x12B and +0x12C encode different dimensions.

This eliminates a previous ambiguity that could have caused the ESP resolver to merge boiler variant and CO instance.

---

## PASS 21 — +0x12A CONTEXT VALUES SHOULD BE MODELED AS A STATE ENUM

The firmware has at least:
context 0,1,2,3,4,5.

The safest reconstruction representation is:

enum UiContextFamily {
  Context0,
  Context1,
  Context2,
  Context3,
  Context4,
  Context5
}

with +0x12B and +0x12C held as separate orthogonal state.

Do NOT expose these raw numeric names to the user-facing UI; they are internal firmware evidence.

---

## PASS 22 — NEW TARGET: RESOLVE THE PRODUCER OF +0x12B = 0x10 / 0x11

Direct setter path:
0x0803C15A -> FUN_08038568 -> +0x12B = 0x10
0x0803C166 -> FUN_0803856C -> +0x12B = 0x11

The dispatcher at 0x0803C064 selects these cases from a lookup table.

Next exact work:
- decode the table at 0x0803C218
- identify which input selector reaches 0x3C15A/0x3C166
- trace upstream caller and semantic source
- connect it to context 3 resource choice

This is now a high-priority resolver target.
