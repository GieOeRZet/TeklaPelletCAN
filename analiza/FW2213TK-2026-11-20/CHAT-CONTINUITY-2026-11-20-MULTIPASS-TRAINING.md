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
