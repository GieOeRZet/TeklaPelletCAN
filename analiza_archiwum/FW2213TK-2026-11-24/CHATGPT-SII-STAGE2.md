# ChatGPT SIEĆ / INFO / INTERNET — dynamic stage 2

Date: 2026-11-24
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071

## Evidence status
Local runtime execution against the canonical firmware produced the measurements below. They are recorded as STRONG dynamic evidence until the exact repository acceptance harness is rerun on the same checkpoint/evidence package. No real boiler/CAN hardware was used.

## SIEĆ
- 0x56: CAN IO BIG, Node ID-86. PDO1 bytes 6/7 = 34 12 displayed as SW v52.1c in the earlier 8-sample run; stabilized 10-round evidence gives v52.18. The stabilized result is authoritative.
- 0x57: CAN IO BIG, Node ID-87, no SW field even with non-zero PDO1 version under the tested scenario.
- 0x5B: VIDE NET WIFI, Node ID-91, SW v0.0.
- 0x45: CAN IO 5, Node ID-69, SW v52.18 in stabilized interpretation, fourth field T=150 in the tested live-data state.
- 0x40/0x46: SW v0.0 and T=150 in the tested live-data state.
- 0x78: CAN IO MINI 0, Node ID-120, SW v0.0, T=-273.
- 9-module test: exactly 8 rows are visible; ordering is by Node-ID with truncation at 8.
- Identity-value changes did not alter the displayed name for the tested 0x56 case, supporting Node-ID based name mapping.
- 10000 ticks without a new heartbeat did not remove the row. Exact offline timeout remains OPEN (>10000 ticks).

## INFO
- 0x3664 is FACT-DYNAMIC as the software-version source when set before entering INFO: 0x0214 -> v2.213 TE; 39321 -> v39.321 TE.
- 0x3665 remains FACT-STATIC as the named parameter igneTouch boiler short name; arbitrary injected values did not change Bio Compact 10kW, so the actual wildcard producer remains OPEN.
- 0x2170 remains FACT-STATIC as VideRoom PIN; injected values did not change videRoom PIN 0, so the actual wildcard producer remains OPEN.
- INFO render trace observed no live PID reads; text IDs and bitmap evidence support pre-population/configuration rather than a simple draw-time PID lookup.

## INTERNET
- SSID editor: 24 characters across 0x3730..0x3735, four characters per u32, with big-endian character packing inside each word.
- PASSWORD is editable; committing A writes PID 0x3736.
- SERIAL/PIN do not open an editor in the tested UI path.
- Widget -> PID binding is FACT-DYNAMIC: SERIAL -> 0x373F, PIN -> 0x3740.
- WiFi switch -> 0x373E; remote-changes switch -> 0x3741; both respond to left/right tap side in the tested UI path.
- SSID persistence was observed after leaving and re-entering the screen.
- 0x5B presence produced no INTERNET body difference in the tested heartbeat/identity/PDO conditions. Classification: NEGATIVE_UNDER_TEST, not universal CLOSED.

## Exact-harness OPEN items
1. Re-run through the repository-native acceptance harness with same-length control runs and committed evidence.
2. INFO: exact producer of boiler name and videRoom PIN wildcard text.
3. INTERNET: full PASSWORD chunk/limit matrix, SERIAL/PIN editor rationale, 0x5B correlation, header status-icon source.
4. SIEĆ: exact offline timeout, exact 0x57 SW omission mechanism, full fourth-column source matrix.
