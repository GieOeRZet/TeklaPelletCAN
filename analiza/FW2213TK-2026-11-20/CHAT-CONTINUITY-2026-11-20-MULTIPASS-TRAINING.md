# CHAT CONTINUITY — 2026-11-20 MULTIPASS / TRAINING CHECKPOINT

## User instruction captured

The user explicitly requested that the conversation context be preserved in the project and that reverse engineering be performed with maximum available resources: many independent passes, multiple analytical levels, and parallel/orthogonal threads rather than a single shallow analysis.

This file is a technical continuity summary, not a literal raw transcript. A raw transcript must not be claimed unless the platform exposes the complete conversation.

## Current project direction

TeklaPelletCAN is a new implementation intended to reproduce the original Estyma/igneoTouch firmware behavior 1:1, except for the physical platform. The original ST hardware is replaced by ESP + CAN. The existing TeklaPelletCAN card is not the behavioral specification.

Source of truth:
- raw firmware /mnt/data/FW2213TK_kopia.bin
- SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## What this conversation added

1. Reconfirmed requirement to preserve conversation continuity in GitHub.
2. Reconfirmed requirement for many independent reverse-engineering passes.
3. Performed a new multi-level configuration/access/menu analysis.
4. Closed configuration internal-index -> CAN mappings.
5. Closed the first configuration visibility resolver.
6. Closed the access/PIN mapping and corrected the previous wrong interpretation of model +0x158.
7. Parsed the raw 21-record resource table at 0x42348.
8. Corrected an overstatement: the constructor at 0x42160 consumes only the first 15 records in its two loops; the trailing six records are still OPEN.
9. Confirmed the main-menu selector semantics for the first 15 records only at STRONG level, with firmware strings/assets used as corroboration.
10. Established the next priority: trace the exact consumer of the trailing six records and trace all 0x158 access-level consumers to concrete screen/menu families.

## Closed firmware facts

### Configuration gates
FUN_0803C178:
- selector 1 -> internal 0x10E -> CAN 0x2105, threshold >=1
- selector 2 -> 0x2105, threshold >=2
- selector 3 -> 0x2105, threshold >=3
- selector 4 -> 0x2105, threshold >=4
- selector 5 -> internal 0x10F -> CAN 0x2106, nonzero
- selector 6 -> internal 0x110 -> CAN 0x2108, nonzero
- selector 7 -> internal 0x111 -> CAN 0x2107, nonzero
- selector 8 -> internal 0x11C -> CAN 0x350C, nonzero
- selector 9 -> internal 0x122 -> CAN 0x3525, nonzero
- other selector values return true at this resolver layer.

### Access
FUN_08042024 converts four decimal digit bytes to a 4-digit number.
FUN_08042328 passes it to FUN_0803C21C -> FUN_08037E74.
FUN_08037E74:
- 0 -> level 0
- 0900 -> level 1
- 0999 -> level 2
- 6154 -> level 3
- other nonzero values leave prior level unchanged.
Result stored in model +0x158.
FUN_08037CA4 initializes +0x158 to 0.

### Raw table
At 0x42348, 21 records, 6 bytes each:
selector, bitmap_A, bitmap_B.
The exact records are documented in BATCH-CONFIG-ACCESS-RESOLVER-MULTIPASS-2026-11-20.md.

### Critical correction
Do not say "21-row menu closed." Only the first 15 records are consumed by the 0x42160 constructor's loops. The trailing six are unresolved.

## Multi-pass method required from here

Every major target should be attacked independently through:
1. raw byte/table scan,
2. disassembly/control-flow,
3. call-site/xref graph,
4. data/record mapper,
5. string catalog,
6. bitmap/resource evidence,
7. widget/class/vtable structure,
8. geometry,
9. touch/callback/write path,
10. configuration gating,
11. access gating,
12. synthetic configuration matrix,
13. contradiction search,
14. stale-hypothesis check,
15. implementation model.

Never silently promote an inference to CLOSED.

## Immediate targets

A. Find consumer of trailing six table records: 0,90,97,100,98,95.
B. Identify exact semantic parent for the first 15 records.
C. Trace FUN_0804BC6C object geometry and child tree.
D. Trace touch callbacks/navigation from each row.
E. Map all +0x158 consumers to concrete widget families and access thresholds.
F. Build a machine-readable capability/menu resolver only after the above distinctions are retained.


---
# 2026-11-20 — CRITICAL MENU SECOND-PASS CORRECTION / LARGE MULTIPASS RESULT

Batch:
`analiza/FW2213TK-2026-11-20/BATCH-MAIN-MENU-ACCESS-SECOND-PASS-21-RECORD-CORRECTION-MULTIPASS-2026-11-20.md`
Commit: `d05254d7a6052c7c1eb80a812a3134ab91c375a7`

## User-requested process rule
The user requires maximum-resource RE: many independent passes, multiple analytical levels, orthogonal threads, contradiction checks, stale-hypothesis checks, and automatic persistence after every major run. This run follows that protocol and **corrects the previous menu interpretation rather than preserving a stale conclusion**.

## Major correction
Previous continuity said:
“constructor consumes only first 15; trailing six remain OPEN.”

That is withdrawn.

Raw code proves:
- first loop consumes 0..14;
- access != 0 enables second loop consuming 15..20;
- r4 is intentionally continued, not reset;
- r5 becomes 21;
- a later pass iterates all 21 row slots with stride 0x274;
- another function iterates all 21 slots against RAM 0x20005F08.

Thus the correct model is a **21-slot row family with access-dependent construction of slots 15..20**.

## Important pointer detail
r10 begins as table-2. After 15 increments it points to record14+4. This is deliberate look-behind alignment:
- r10+2 -> next record’s A field,
- r10+4 -> next record’s B field,
- r10[0] -> previous record’s B field.

The 0x0C/0x0E comparison is therefore a look-behind field test, not proof of selectors 12/14.

## New architectural fact
The 21 row objects are stored at:
```
object + 0x380 + n*0x274, n=0..20
```
and FUN_0803C178(model,n) is applied to every slot afterward.

A separate function at 0x422C8 iterates the same 21-slot structure and consults a runtime byte array at RAM 0x20005F08, gated by access state.

## Status
CLOSED:
- full 21-record consumption path;
- access-dependent second-stage construction;
- 21-row-object stride/base;
- 21-slot capability pass;
- 21-slot access/update pass existence.

OPEN:
- row class/vtable;
- exact child tree and geometry;
- selectors 0/90/97/100/98/95 semantic destinations in the second stage;
- RAM 0x20005F08 producer/meaning;
- touch/navigation callbacks;
- FUN_08032F08 / FUN_0803C270 exact semantics.

## Mandatory next passes
1. raw xrefs/writers of 0x20005F08;
2. control/data flow FUN_08032F08;
3. control/data flow FUN_0803C270;
4. row object constructor/vtable and children;
5. selector navigation/touch;
6. geometry/clipping/visibility;
7. contradiction/stale-hypothesis check;
8. synthetic access x capability matrix.


---
# 2026-11-20 — PIN / ACCESS MULTIPASS RESULT

Batch:
`analiza/FW2213TK-2026-11-20/BATCH-PIN-ACCESS-AND-RESET-MULTIPASS-2026-11-20.md`
Commit: `99e32ac4e5c2c0ebed6862411ae8121e91fbf707`

## USER OBSERVATION CONFIRMED BY RAW BIN

The user's tier model is correct:
- level 0 base
- 0900 -> level 1
- 0999 -> level 2
- a further level exists.

Firmware closes the third code:
- 6154 -> level 3.

The mapping is implemented by `FUN_08037E74`, storing level at +0x158.

## SPECIAL CODES

Separate from access levels:
- 1992
- 6666

6666 writes special flag +0x07. The exact reset sequence is still OPEN.

## METHODOLOGY

This batch used independent passes over:
- raw PIN digit decoder;
- callback/control flow;
- access mapping;
- decimal/hex cross-check;
- invalid-code behavior;
- global has-access state;
- special-code handler;
- 6666 downstream consumer;
- 1992 path;
- all direct callers;
- immediate-constant search;
- contradiction/stale-hypothesis checks.

Do not collapse special codes into access levels.

## NEXT

Prioritize 6666 -> Default settings request -> persistence/reset path, then boiler-dependent PIN mechanism.


---
# 2026-11-20 — 6154 / LEVEL 3 MULTIPASS RESULT

Batch:
`analiza/FW2213TK-2026-11-20/BATCH-6154-LEVEL3-UI-GATES-MULTIPASS-2026-11-20.md`
Commit: `12efc1b11136f559bcdd33093cfc99c85a25bf19`

User asked what "6164" does. Raw firmware corrects this to 6154.

Independent passes closed:
- fixed code constant;
- decimal/hex conversion;
- access-level storage;
- all direct +0x158 level-3 comparisons;
- 17 distinct gate locations;
- child-tree insertion;
- common event handler;
- + / - semantics;
- comparison against 0900/0999 behavior;
- contradiction and stale-hypothesis check.

New architectural fact:
6154 is not only a menu visibility level. It adds an increment control to a family of parameter-editor/setup screens.

Still OPEN:
- exact screen labels;
- exact parameter binding per gate;
- exact CAN/write side effect;
- whether these are all service/installer functions or a mixture of normal editors with elevated adjustment capability.
