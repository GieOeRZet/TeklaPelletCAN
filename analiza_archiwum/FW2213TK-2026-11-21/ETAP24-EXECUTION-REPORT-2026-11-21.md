# TEKLAPELLET-CAN — ETAP 24 EXECUTION REPORT

**Data:** 2026-11-21  
**Repo:** GieOeRZet/TeklaPelletCAN  
**Branch:** ccr-be8a1bcb-5t76j0  
**Firmware:** FW2213TK_kopia.bin  
**Size:** 0x1F0000 B = 2,031,616 B  
**SHA-256:** 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## STATUS

[NEW-HARD] Supplied etap24_full_dump.py was executed directly against the physical firmware. Exit code: 0.

Execution result:
DONE: ETAP24_RAW_DUMP.zip | rows=188 | ui_id_hits=21

The required ZIP contains exactly 3 files:
- caller_08010F80_08011040_and_init_08000D40.txt — 16,081 B
- can_080635B0_080636A0_and_08063D40_08063E10.txt — 1,562 B
- resource_188_summary_and_can_ids.csv — 15,716 B

ZIP size: 7,929 B.

## P1 — caller / initialization

[NEW-HARD] Whole-BIN direct BL scan for targets 0x08010FB0..0x08011040 was executed and preserved in the raw output. The returned list contains numerous direct callers, predominantly to 0x08010FC2.

[CONFIRMED-REPEAT] Raw windows were extracted for:
- 0x08010F80..0x08011040
- 0x08000D00..0x08000E40
- 0x0800FF40..0x0800FF60

The supplied script intentionally emits raw bytes plus its own direct-BL decoder; no mnemonic disassembly was substituted.

## P2 — CAN windows

[NEW-HARD] Raw windows:
- 0x080635B0..0x080636A0
- 0x08063D40..0x08063E10

The second window produced 6 decoded direct BLs:
- 0x08063D4E -> 0x08015104
- 0x08063D68 -> 0x08015198
- 0x08063D70 -> 0x08015104
- 0x08063D98 -> 0x08015310
- 0x08063DB2 -> 0x08015260
- 0x08063DEE -> 0x08063EAA

[OPEN] The requested regions around 0x080635F2 / 0x08063648 are preserved as raw bytes. This script decodes direct BL only, so no additional claim is made about possible indirect BLX calls there.

## P3 — 188 resources / UI ID scan

[CONFIRMED-REPEAT] Exactly 188 resource records were exported from DAT_0804866C using corrected TypedText base 0x5BE64.

[NEW-HARD] The MOVW scan over 0x08031E00..0x08041600 found exactly 21 matches whose immediate is one of the 188 resource IDs.

Examples:
- 0x08031EB4: #0x010F -> Ciepła woda użytkowa
- 0x0803219A: #0x0149 -> Rezerwa zbiornika paliwa [kg]
- 0x08032960: #0x011D -> Czujnik ciśnienia
- 0x0803C80E: #0x0153 -> Opóźn. zwiększ. stopnia mocy [min]
- 0x0803CB9A: #0x011F -> Pomiar energii
- 0x0804024E: #0x010D -> Temperatura maksymalna wody / candidate resource context

The script also generated ui_write_id_candidates.txt as a sidecar, but the Etap 24 specification requires that ZIP contain only the three files above; therefore the sidecar is not in the ZIP.

Important: the 21 MOVW hits are ID candidates, not proof that each site performs a parameter write. Context/callgraph analysis remains OPEN.

## INTEGRITY

[CONFIRMED-REPEAT]
- Firmware size assertion passed.
- Firmware SHA assertion passed.
- Script return code: 0.
- ZIP contains exactly the required 3 result files.

## NEXT PRIORITIES

[OPEN] Resolve which of the 21 UI resource-ID candidates are actual parameter-write sites and connect them to FUN_08037212 -> FUN_08011812.

[OPEN] Resolve indirect BLX/vtable paths around the CAN windows and connect them to the already established 0x0604 TX mechanism.

No new CANopen/SDO semantic label is asserted by this execution report.
