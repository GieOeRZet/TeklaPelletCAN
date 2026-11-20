# MULTIPASS-13 — 6154 / NUMERIC-CONTROL → UI-FAMILY → PARAMETER-BINDING DEEP AUDIT
Date: 2026-11-20
Base state: 5add5f0ef67d397705716e383805d991d92b7368

## User directive carried into this run
Continue without stopping on a single finding. Use many independent passes, multiple levels and branches, and persist continuity after each major run. The goal is a solid reconstruction of original FW2213TK behavior, not a shallow menu approximation.

## Run design
This run deliberately used independent axes:
1. 6154 gate revalidation.
2. 17-wrapper/caller revalidation.
3. constructor/context-source audit.
4. widget-resource audit.
5. TypedText/title audit.
6. +0x23C/+0x284 event semantics.
7. +0x60/+0x64 taint-boundary audit.
8. +0x140 numeric-widget target audit.
9. +0x3D8 virtual-object audit.
10. vtable architecture cross-check.
11. +0x12A context enumeration.
12. +0x12B class/variant consumer audit.
13. +0x12C instance audit.
14. C064/D00 classification chain audit.
15. E714 Heating UI consumer audit.
16. 36FF2/370C0/37212 parameter-engine audit.
17. configuration resolver 10E/10F/110/111 cross-check.
18. registry/record dispatcher cross-check.
19. bitmap/resource-family cross-check.
20. stale-hypothesis / evidence-boundary audit.

## New/strengthened result A — 4A510 is now concretely anchored to a real UI label
The existing firmware trace identifies:
- parent method around 0x0804A114;
- setup wrapper FUN_0804A510;
- conditional child parent+0x23C at access >=3;
- parent+0x23C is TypedText ID 454 (0x1C6);
- ID 454 text is "Próg zmniejszania stopnia mocy [%]";
- geometry of that child is X=439, Y=0, W=40, H=30.

This is a much stronger identification than merely calling +0x23C a generic '+' control. The same wrapper is therefore part of a concrete UI component whose level-3 addition is an editor control associated with the "Próg zmniejszania stopnia mocy [%]" field.

Important: this does NOT yet prove that all 17 wrappers represent the same parameter. It proves the concrete identity of this branch/component and gives a template for resolving the remaining 16.

## New/strengthened result B — wrapper family extends beyond the 17 setup entry points
A separate constructor/layout audit records repeated sibling setup methods:
- 0x0804E7A4
- 0x0804FF64
- 0x08050220
- 0x080504DC
- 0x08050798
- 0x08050AAC
- 0x08050D68
- 0x08051024
- 0x080512E0

They repeat substantially the same layout and differ in their downstream helper. This supports treating the 17 level-3 sites as members of a component family, while still requiring per-instance binding before assigning semantics.

## New/strengthened result C — 6154 is a control-tree permission, not a parameter selector
The independent event audit remains:
- +0x23C = increment/+ target.
- +0x284 = decrement/- target.
- +0x60 changes within [1, +0x64].
- FUN_08035786 is geometry/value interpolation and is NOT a proven CAN writer.

Therefore the 6154 gate changes whether the numeric editor's interactive child exists. It does not itself identify the underlying parameter.

## New/strengthened result D — the real parameter path is already available downstream of the UI
Independent pre-6154 traces close the following architecture:
- +0x12B selects a class/UI family.
- +0x12C selects an active instance.
- FUN_08036FF2 performs instance-aware parameter lookup.
- FUN_080370C0 and FUN_08037212 provide corresponding read/write-side instance indexing.
- FUN_0803E714 consumes +0x12B values 1..4 as one shared Heating UI branch.
- that branch creates a parameter-ID list and resolves each ID through FUN_08036FF2.
- known four-instance parameter families include 0x2032..0x2035, 0x2048..0x204B and 0x2064..0x2067.

This means the next useful merge is not "6154 -> CAN" directly. It is:
6154 -> numeric widget -> page/component binding -> panel parameter ID -> FUN_08036FF2 -> instance-aware record -> CAN/SDO layer.

## New/strengthened result E — configuration must remain orthogonal
FUN_0803C178 and related traces independently establish configuration gates:
- selector 5 -> internal 0x10F -> CWU configuration;
- selector 6 -> 0x110 -> solar;
- selector 7 -> 0x111 -> buffer;
- selectors 1..4 -> 0x10E -> heating/CO configuration.

Existing parameter/CAN mapping evidence:
- 0x10F -> CAN 0x2105
- 0x110 -> CAN 0x2107
- 0x111 -> CAN 0x2106
- 0x114 -> CAN 0x2108

Do not merge these with +0x12C or with the 6154 permission gate.

## Negative findings retained
- +0x12A is not a parent field; it is a byte in the global/application context.
- +0x12B is not simply the active CO instance.
- +0x12C is not a generic menu number; it is consumed as an instance dimension.
- 0x3D8 is NOT yet proven to be a CAN writer.
- FUN_08035786 is NOT a CAN writer.
- 0x2105 is NOT yet proven to be the source of C064 object creation.
- DAT_0804107C/0x08040FC2 remains classified as Test I/O, not the main CO activation bridge.
- repeated resources 0x28..0x31 are NOT yet safely translated into human labels.
- geometry is evidence, not the primary behavioral specification.

## Priority graph after this run

### Branch A — 6154 component identity
4A510 / sibling wrappers
 -> parent class/vptr
 -> +0x23C TypedText/resource
 -> +0x60/+0x64 initialization
 -> numeric widget object
 -> parameter ID

### Branch B — instance-aware parameter engine
parameter ID
 -> FUN_08036FF2 / 370C0 / 37212
 -> +0x12C
 -> concrete record family
 -> storage/descriptor
 -> CAN/SDO

### Branch C — virtual callback
parent+0x3D8
 -> object
 -> vtable +0x08/+0x0C
 -> model/record operation
 -> exact write/update side effect

### Branch D — object classification
indirect C064 entry
 -> param_2
 -> DAT_0803C218[param_2]
 -> class/type
 -> +0x12B
 -> FUN_08037D00
 -> +0x12C

### Branch E — page-family/configuration
+0x12A/+0x12B/+0x12C
 + configuration resolver
 + access level
 -> concrete page/widget tree

## What this run closes
The 6154 analysis now has a concrete semantic anchor for at least one wrapper/component: 4A510's +0x23C is the actual level-3 numeric editor child associated with TypedText 454 / "Próg zmniejszania stopnia mocy [%]". This is the first direct bridge from the generic 17-wrapper gate to a human-readable parameter label.

## What remains open
1. Exact +0x60 source and +0x64 limit for 4A510 and the other 16.
2. Exact panel parameter ID behind +0x60 for each component.
3. Exact +0x3D8 assignment and vtable targets.
4. Exact mapping of the remaining 16 wrappers to titles/resources/parameter families.
5. Exact C064 indirect entry and DAT_0803C218 contents.
6. Exact raw table contents DAT_0803EEC0 and DAT_0803C218.
7. Exact CAN/SDO side effect for each newly exposed numeric editor.

## Required next multipass attack
Do NOT stop at 4A510. The next run should build a 17-row matrix and, for each wrapper, independently recover:
constructor -> parent vptr -> child +0x23C -> TypedText/bitmap -> numeric object -> +0x60/+0x64 -> panel parameter ID -> FUN_08036FF2 -> instance -> CAN/SDO.

If a direct edge is missing, mark it OPEN and attack it from the reverse direction (parameter -> UI), not by guessing from label or geometry.

## Evidence policy
[FW] direct firmware/decompiled evidence.
[STRONG] multiple independent traces converge.
[OPEN] unresolved.
[REJECTED] explicitly withdrawn hypothesis.

No raw transcript is claimed here.
