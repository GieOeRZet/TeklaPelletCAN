# ChatGPT SIEĆ / INFO / INTERNET — dynamic stage 2

Date: 2026-11-24
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Runtime note
Tests were executed locally against the canonical firmware using the reconstructed runtime core from the repository tools. Results are recorded as STRONG dynamic evidence until the exact repository acceptance harness is rerun on the same evidence. No real boiler/CAN hardware was touched.

## SIEĆ
- 0x56: CAN IO BIG, Node ID-86. PDO1 bytes 6/7 changed displayed SW: 34 12 -> SW v52.1c; 78 56 -> SW v120.c.
- 0x57: CAN IO BIG, Node ID-87, but no SW field even with non-zero PDO1 version.
- 0x5B: VIDE NET WIFI, Node ID-91, SW v0.0.
- 0x45: CAN IO 5, Node ID-69, SW v52.1c, fourth field T=150.
- 0x40: CAN IO 0, Node ID-64, SW v0.0, T=150.
- 0x46: CAN IO 6, Node ID-70, SW v0.0, T=150.
- 0x78: CAN IO MINI 0, Node ID-120, SW v0.0, T=-273.
- 0x50, 0x54, 0x55, 0x7A..0x7D: no fourth column observed.
- 9-module test: exactly 8 rows visible. Forward order omitted 0x50; reverse order omitted 0x40 and showed 0x50, consistent with a sorted list capped at 8 rows.
- Identity test: heartbeat alone produced a row for 0x56; changing SDO identity to 0x11223344 or 0xAABBCCDD did not change the name. Name follows Node-ID mapping.
- 10000 ticks without new heartbeat did not remove the row. Exact offline timeout remains OPEN.

## INFO
- Vtable 0x808f638.
- L0 vs L1: only header access icon changes (person vs key); body remains identical.
- 0x3664 proven as software-version source when set before entering INFO: 2213 -> v2.213 TE; 39321 -> v39.321 TE.
- 0x3665 arbitrary values tested did not alter Bio Compact 10kW; direct source remains OPEN.
- 0x2170 changed before entry did not alter videRoom PIN 0; direct source remains OPEN.
- INFO render trace observed no live PID reads; text IDs observed (PL,109) and (CZ,14), bitmap 79. This supports pre-population/constructor/config sourcing rather than a live draw-time PID lookup.
- Static text confirmed: INFO and Controller by Estyma (www.estyma.pl).

## INTERNET
- SSID editor uses 0x3730..0x3735, four characters per u32, big-endian within each u32.
- A -> 4230370100000041
- AB -> 4230370100004241
- ABC -> 4230370100434241
- ABCD -> 4230370144434241
- ABCDE -> 4231370100000045
- < deletes the last committed character; after ABC it writes the AB representation.
- 24 characters accepted; 25th/26th generate no 0x584 write.
- Character sets: A-Z (26), a-z (26), 0-9 (10), and 33 ASCII symbols 0x21..0x7E excluding space.
- Cancel paths tested: < on empty, tap outside keyboard, top-left MENU after uncommitted character; no 0x584 write.
- PASSWORD editable; committing A wrote PID 0x3736.
- SERIAL and PIN did not open an editor in the tested UI path.
- WiFi 0x373E: right/on-side writes 1; left/off-side writes 0.
- Zmiany zdalne 0x3741: same on/off-side behavior.
- SSID persistence proven across exit to MENU and re-entry.
- 0x5B presence did not change INTERNET body in the tested conditions; exact correlation OPEN.

## Remaining exact-harness OPEN
1. Re-run through exact repo acceptance harness with same-length control runs and repo-native evidence.
2. INFO: full-range PID diff and exact source of boiler name/PIN/trailing zero.
3. INTERNET: full PASSWORD multi-chunk/limit matrix; SERIAL/PIN rationale; 0x5B correlation; header status icon source.
4. SIEĆ: exact SW formatting algorithm, 0x57 SW omission mechanism, fourth-column source matrix, exact offline timeout.
