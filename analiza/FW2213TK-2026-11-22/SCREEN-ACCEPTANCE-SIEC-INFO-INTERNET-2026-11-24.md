# SCREEN ACCEPTANCE — SIEĆ / INFO / INTERNET

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Cel: doprowadzić trzy ekrany do tego samego standardu dowodowego co Test wyjść: deterministyczny przebieg, baseline, akcja, obserwacja framebuffer/PID/CAN/vtable, przypadki brzegowe i zamknięcie OPEN. Nie oznaczać UNKNOWN jako FACT-DYNAMIC bez wykonania testu.

## 1. SIEĆ — vtable 0x808f770

### HARD obecnie
- Menu row 19, poziom minimalny 1.
- Oficjalna dokumentacja Estyma: ekran pokazuje stan podłączonych modułów sieci CAN.
- Jedna znana konfiguracja bez partnerów: lista wierszy jest pusta.
- Layout: nagłówek + kontener 460x232; 8 slotów po 28 px.
- Kolumny: x=15/150/260/340, szerokości 135/110/80/90. Semantyka kolumn pozostaje OPEN.
- Node map:
  0x05..0x07 SLAVE 1..3
  0x08 RADIO GATEWAY
  0x40..0x47 CAN IO 0..7
  0x50 MODUL LAMBDA
  0x51 IO BOARD PRO
  0x54/0x55 FLOWMETER 1/2
  0x56/0x57 CAN IO BIG
  0x5A VIDE GSM
  0x5B VIDE NET WIFI
  0x5C VIDE NET
  0x64..0x67 VIDE ROOM 1..4
  0x6E..0x75 CAN GATEWAY 0..7
  0x78..0x7F CAN IO MINI 0..7
  unknown -> fallback UNKNOWN.
- Discovery traffic already established: heartbeat 0x701..0x77F; SDO responses 0x581..0x5FF; identity request 0x600+node, payload 40 18 10 02.

### Acceptance matrix
T0 empty bus -> exact 8-row blank state.
T1 node 0x56 only -> row count/order + all 4 fields.
T2 node 0x57 only -> same.
T3 nodes 0x56+0x57 -> prove two entries and order.
T4 one node from every known node family -> label + all four fields.
T5 unknown node ID -> prove UNKNOWN/fallback or prove identity-dependent label.
T6 known node with wrong/missing identity -> distinguish Node-ID mapping from 0x1018 identity.
T7 heartbeat timeout -> exact disappearance/retention time.
T8 simultaneous nodes -> ordering rule (Node-ID, discovery order, table order, or other).
T9 node reappears -> whether row is reused or appended.
T10 status/version changes -> determine status column and version column.
T11 0x5B VIDE NET WIFI -> cross-correlate with INTERNET state.
For each test save BEFORE.png, AFTER.png, diff.png, CAN RX/TX JSON, vtable, row OCR/text/widget trace.

### Closure criteria
All four columns have proven semantics; row ordering is proven; appearance/disappearance rule is proven; known/unknown/identity behavior is proven; status/version formatting is proven.

## 2. INFO — vtable 0x808f638

### HARD currently
Widgets:
- '<' at (12,6), 9x25, bitmap/text navigation.
- header bitmap 92 at (390,9), 39x23.
- touch header/back region.
- title INFO at (221,10).
- software: (40,50), text 82, 'igneoTouch v' + value; observed 2.213 TE.
- boiler: (40,82), text 492; observed Bio Compact 10kW.
- VideRoom PIN: (40,114), text 492; observed 'videRoom PIN 0'.
- second header-level variant differs in header icon.
Known PID mapping:
- 0x3664 = software version, u16.
- 0x3665 = boiler short name, u32.
- 0x2170 = VideRoom PIN, u16, runtime default catalog 5678.
Producer text is static: Controller by Estyma (www.estyma.pl).

### Acceptance matrix
I0 baseline with canonical/default values.
I1 change 0x3664 one value -> exact text update + formatting.
I2 change 0x3665 -> exact name formatting, width/truncation.
I3 change 0x2170 -> exact PIN formatting including 0, 1, 4, 5 and max values.
I4 cross-check live CAN update vs direct storage state.
I5 header level 0/1/2/3 -> exact icon/CPU indicator behavior.
I6 verify static producer text is unaffected by PID changes.
I7 navigate back -> exact vtable and framebuffer restoration.
I8 repeated enter/exit -> no stale value, no duplicated widget, no extra CAN.
I9 language change -> all static/dynamic strings and formatting.
Every case: BEFORE/AFTER/diff, PID storage, CAN, text trace, bitmap trace, vtable.

### Closure criteria
Every dynamic field mapped to PID/type/formatting and update trigger; every header variant proven; no OPEN behavior.

## 3. INTERNET — vtable 0x808f9ac

### HARD currently
Screen fields:
- title INTERNET at (200,10), text 59.
- SSID label/value at y=50, touch region x=35..350.
- PASSWORD, SERIAL, PIN, WiFi, Zmiany zdalne.
- WiFi signal/status bitmaps include 153/154.
- SSID PID 0x3730..0x3735 = six u32 parts, 24 chars, big-endian bytes per u32.
- KEY 0x3736..0x373B = six u32 parts.
- 0x373C/0x373D status; 0x373D=2 observed to show WiFi icon.
- 0x373E WiFi switch.
- 0x3741 Zmiany zdalne switch.
- 0x373F SERIAL u32.
- 0x3740 PIN u32.
- 0x3744/0x3745/0x3746 auxiliary visual/status flags.
- presenter cluster 0x0804DA00..0x0804DD56.
- panel has no active WiFi peripheral; INTERNET config belongs to external CAN module, known node 0x5B = VIDE NET WIFI.

### Acceptance matrix
N0 baseline with all zero/status variants.
N1 set SSID 'Home' -> prove exact 6-part encoding.
N2 set 24-char SSID -> prove full boundary.
N3 set 25-char source -> prove truncation/rejection/overflow behavior.
N4 set empty SSID.
N5 characters: space, digits, underscore, dash, dot, Polish/non-ASCII, symbols -> exact accepted encoding.
N6 tap SSID -> identify dialog vtable, widget inventory and editor buffer.
N7 editor: append, delete/backspace, cursor movement, clear, OK, cancel.
N8 editor: exact character-to-PID-part mapping and save timing.
N9 repeat N6-N8 for PASSWORD.
N10 WiFi 0->1 and 1->0 -> exact PID/CAN/framebuffer.
N11 Zmiany zdalne 0->1 and 1->0 -> exact PID/CAN/framebuffer.
N12 vary 0x373C,0x373D,0x3744,0x3745,0x3746 independently and in combinations -> exact icon/color/status truth table.
N13 SERIAL values 0,1, max -> exact formatting.
N14 PIN values 0,1, max -> exact formatting.
N15 save/re-enter -> prove persistence and no stale editor state.
N16 invalid/partial editor close -> prove commit/cancel semantics.
N17 external 0x5B module present/absent -> correlate status/icon and SIEĆ row.
For every test save BEFORE/AFTER/diff, vtable, widget inventory, text trace, bitmap trace, PID changes and all non-background CAN frames.

### Closure criteria
Keyboard/editor is completely identified; SSID/KEY serialization and limits are proven; every switch/status bit has proven visual semantics; save/cancel behavior and CAN writes are proven; 0x5B correlation is proven.

## Evidence rules
FACT-DYNAMIC only after actual firmware-emulator execution and observed output.
FACT-STATIC only from firmware/repository evidence.
INFERENCE remains explicitly labelled.
OPEN remains until acceptance test closes it.
Never infer SIEĆ column semantics from shared TypedText IDs 471..474; those IDs are used elsewhere.

## Required artifacts
For each screen:
- *_acceptance.json
- baseline.png
- per-test before/after/diff PNG
- CAN trace JSON
- widget/text/bitmap trace JSON
- final *_CLOSURE.md with 0 OPEN items.

## Current status
This file is the execution specification. It intentionally does not claim completion where the dynamic acceptance tests have not yet been run.
