# TEKLAPELLET-CAN — MASTER CONTEXT ETAP 1–38 / P0–P6

Firmware: `FW2213TK_kopia.bin`  
Size: `0x1F0000` (2,031,616 B)  
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

This document extends `MASTER-CONTEXT-ETAP1-30-ESP32C6.md`. Evidence labels: **[NEW-HARD]**, **[CONFIRMED-REPEAT]**, **[NEW-STRONG]**, **[OPEN]**, **[REJECTED]**. RAW BIN/RAW dumps remain the source of truth.

## 1. Confirmed CAN2 facts

**[CONFIRMED-REPEAT] CAN2:** `0x40006800`.

RX:
- storage `0x200244BC`
- handle `0x200244DC`
- producer `0x0806F9F8 → FUN_080617DC`
- consumer `CanRxTask @ 0x0806E94C → FUN_08063B80`

TX:
- storage `0x200244E0`
- handle `0x200244EC`
- queue primitive `0x08057224`
- consumer `CanTxTask @ 0x080654A8`
- hardware TX `FUN_08061734(0x40006800, record)`

**[NEW-HARD]** `0x08057224` is FreeRTOS queue-send machinery, not the CAN protocol itself.

### EstymaCanFrame — 20 bytes

**[NEW-HARD]**
| Offset | Meaning |
|---|---|
| +0x00..+0x03 | StdId u32 |
| +0x04..+0x07 | ExtId u32 |
| +0x08 | IDE, raw 0x04 |
| +0x09 | RTR, raw 0x02 |
| +0x0A | DLC = RDTR & 0x0F |
| +0x0B..+0x12 | Data[0..7] |
| +0x13 | RX metadata = RDTR >> 8 |

RX mailbox registers: RIR +0x1B0, RDTR +0x1B4, RDLR +0x1B8, RDHR +0x1BC. StdId = RIR >> 21, ExtId = RIR >> 3. TX writes TIR/TDTR/TDLR/TDHR and requests transmission.

## 2. RX dispatcher

Main path:
`CAN2 RX → FUN_080617DC → ReceivedCanMessages → CanRxTask → FUN_08063B80 → 12 handler families`

Families:
`0x0800E2D2, 0x0800DFC6, 0x08063E10, 0x08063F30, 0x0800FEB4, 0x0800FF50, 0x0800F894, 0x0806369E, 0x0800F0D0, 0x08062A90, 0x08063FBA, 0x08064008`.

Known filters include base +0x180/+0x280, +0x380/+0x480, +0x600, +0x584, +0x1EE, absolute 0x0584, ranges 0x0701..0x077F and 0x0581..0x0600, 0x0288 and StdId 0x0240..0x0257.

**[OPEN]** Semantics of the remaining RX families are not complete.

## 3. Parameter engine

### FUN_08011812

**[CONFIRMED-REPEAT]**
- parameter lookup and type check;
- writes through `record+0x0C`;
- types 1..5;
- `param_5 != 0`: state check;
- `param_6 == 1`: range validation.

For `param_5=1`: `record = base + index*0x2C`; `record+0x2C` must be 0x01 or 0x03, else status 0x09.

**[REJECTED]** It is not proven to be a dirty-bit setter and does not itself call 0x0806E59C, 0x08057224, send CAN, or execute a confirmed TX callback.

### FUN_08037212

**[CONFIRMED-REPEAT]** 33 direct UI callers.

Confirmed local path:
`UI → FUN_08037212 → FUN_08011812 → parameter record +0x0C → local RAM`.

**[OPEN]** local parameter write → CAN TX bridge.

### FUN_08062B22

Confirmed:
`CAN frame → 0x08062AE4/handler → FUN_08062B22 → index frame+4/+5 → FUN_080115F6 → type → FUN_08011812 → record+0x0C`.

Types: 1=1 B, 2=16-bit, 3=32-bit, 4=signed 16-bit, 5=32-bit.

## 4. 0x0604 / 0x0584

Object `0x200114C0`, constructor `FUN_0800FF44`:
- +0x00 = r1, TX adapter
- +0x04 = r2, parameter table
- +0x08 = 4, Node ID

**[OPEN]** exact runtime initialization of +0.

### READ

**[NEW-HARD / CONFIRMED-REPEAT]**
- poller `0x080629FC`
- vtable `0x08094508`, slot 8 → `0x080629FC`
- path `0x080629FC → table + counter*0x2C + 0x08 → 0x08062AE4 → CAN frame`
- StdId 0x0604
- DLC 8
- Data[3] 0x40
- Data[4..5] parameter index
- Data[6] 0x01
- known example index 0x2001

Do not automatically call this CANopen/SDO.

### TX wrapper

`FUN_0806E59C` builds a local record, gets `CanMessagesToTransmit` from `0x200244EC`, sends through `0x08057224`, and has control related to 0x0604.

Literal pool:
- `0x0806E60C → 0x2002466C`
- `0x0806E610 → 0x200244EC`

Vtable `0x08094508`: slot 5 → `0x0806E59C`, slot 8 → `0x080629FC`.

### WRITE / RESPONSE

Observed commands:
- 0x20 write
- 0x40 read
- 0x42 response with value
- 0x60 acknowledgement
- 0x80 error

Specific analyzed path: request write on 0x0604, response/publication on 0x0584, index 0x3004 / subindex 0x01.

Not a complete protocol catalogue.

### FUN_0800FF50

Confirmed:
`StdId == object+0x08+0x600`
→ `(data[3] >> 5)==1 or 2`
→ index=data[4..5]
→ type=data[6]
→ value=data[7..]
→ FUN_080115F6
→ type lookup
→ FUN_08011812
→ response
→ object 0x200114C0
→ vtable slot 0
→ BLX.

**[NEW-HARD]** final dispatch is slot +0x00 of the vtable referenced through field +0 of object 0x200114C0. Raw instructions at 0x080100BE..0x080100C6 establish the slot-0 dispatch.

Response uses base object+0x08+0x580 and contains command/status/index/type/value/result.

## 5. Resources / UI

`DAT_0804866C`:
- exactly 188 records, idx 0..187
- 16 B/record
- raw 0x4866C..0x4921C
- type distribution: 0=139, 1=31, 2=3, 3=12, 4=1, 5=2
- f07: 0x00=148, 0x01=40

ETAP30 produced `esp32_resources_188.json`.

**[CONFIRMED-REPEAT] TypedText base = `0x5BE64 = 0x5BD80 + 57*4`. Do not use old 0x5BD80.**

`FUN_080480C0`:
- resource table records are 16 B;
- type controls dispatch;
- widget base = param_1 + 0x42C;
- widget stride = 0x338;
- relevant fields around +0x334 and +0x270;
- type 1 → FUN_0804E598
- type 2 → FUN_0804E740
- type 3 → FUN_0804E75A
- type 5 → FUN_0804E740
- final FUN_0804E5BC(widget,10).

**[OPEN]** complete resource → TypedText/Bitmap/callback/widget mapping.

## 6. P0–P6 / ETAP31–38

### P0 — ETAP31–32
RAW material for:
`0x200114C0 → [obj+0] → vptr → slot 0 → TX adapter → 0x200244EC → CanTxTask → FUN_08061734 → CAN2`.

ETAP31: xrefs to 0x200114C0 and 0x200244EC plus RAW windows for receiver/TX/CanTxTask/hardware TX.

ETAP32: RAW around 0x08010000..0x080100D0, 0x08000D60..0x08000DB0 and 0x0806E580..0x0806E630.

**[OPEN]** exact slot-0 BLX target and full TX adapter.

### P1 — ETAP33
RAW for the 11 RX families other than 0x0800FF50.

**[OPEN]** family semantics.

### P2 — ETAP34
RAW:
- 0x080629FC..0x08062B50
- 0x080635B0..0x080636A0
- 0x0806E59C..0x0806E640
- 0x0800FF50..0x080100D0

Input for frame/parameter catalogue. Dump alone does not establish semantics.

### P3 — ETAP35
RAW:
- 0x08037210..0x080372C0
- 0x08011810..0x080119F0
- 0x08010FD0..0x08011050

Input for local parameter write path.

### P4 — ETAP36
Selected DAT_0804866C records:
0, 1, 9, 13, 17, 29, 80, 81, 82, 99, 127, 128, 129, 131, 139, 146, 150.
Subtables 0x0807F5DC..0x0807F680.

### P5 — ETAP37
RAW UI-build/configuration area 0x080482C0..0x0804866C immediately before DAT_0804866C.

### P6 — ETAP38
RAW tails:
- 0x08062B20..0x08062BC0
- 0x08011A00..0x08011A60

**[OPEN]** full semantic catalogue still requires instruction/xref analysis and live CAN validation.

## 7. OPEN-1..7

1. **OPEN-1:** 0x200114C0 → [obj+0] → vptr → slot 0 → exact BLX target → TX adapter → 0x200244EC → CanTxTask → FUN_08061734 → CAN2.
2. **OPEN-2:** full semantics of remaining 11 RX families.
3. **OPEN-3:** complete CAN catalogue: ID/DIR/CMD/INDEX/SUB/TYPE/VALUE/RESPONSE/SIDE EFFECT/EVIDENCE.
4. **OPEN-4:** full UI → CAN TX bridge.
5. **OPEN-5:** resource ID ↔ parameter index ↔ CAN index/subindex ↔ local RAM.
6. **OPEN-6:** RAM region 0x20005EF0..0x20005F5B.
7. **OPEN-7:** full resource/widget/TypedText/Bitmap/callback mapping.

## 8. UI-OPEN-1..10

1. meaning of 0x47/0x48;
2. full role of 0x0807F5EC;
3. actual Family-B gate: 2268 / 226E / 226F / 2275 / 227A;
4. full 0x300B → writer → storage → CAN;
5. 2105 → CO capability → object construction → C064 → instance;
6. consumer graph 174/175/176/179;
7. consumer graph 144/145;
8. consumer graph 115;
9. exact Home factory/root;
10. exact Touch rectangles and Home callbacks.

These are open topics, not claims that every partial dependency is unknown.

## 9. [REJECTED] hypotheses

- 0x68 = extra-fan gate — rejected; path is 0x300B → Stop burning wood.
- 0x10E = 0x3505 — rejected; 0x10D → 0x3505, 0x10E → 0x2105.
- 0x10F = 0x2105 — rejected; 0x10F → 0x2106.
- 47290 = graph.
- 47290 = Home seven horizontal zones.
- 056/057 = 151/152.
- Bitmap ID = widget ID.
- 370A 1/2/3 → bitmap 011/012/013.
- 174 = Home-only.
- semantic meaning of 0x47/0x48 from numbering alone.
- FUN_08011812 as standalone dirty-bit/TX setter.
- 0x08078578 = 0x08094508 vtable.

## 10. Other confirmed structures

### VTABLE 0x08094508
slot 5 → 0x0806E59C; slot 8 → 0x080629FC.

### VTABLE 0x08078578
+0x00 → 0x080314C2  
+0x04 → 0x08031792  
+0x08 → 0x080317A0  
+0x0C → 0x08031A74  
+0x10 → 0x0806FC7C  
+0x14 → 0x080894D4  
+0x28 → 0x080314D4

### Poller objects
0x0800DCD4 creates four 0x080702DC instances:
0x200208EC, 0x200209C4, 0x20020A9C, 0x20020B74.
Subobjects +0x30:
0x2002091C, 0x200209F4, 0x20020AD0, 0x20020BA4.

**[NEW-STRONG]** Four poller-bearing subobjects are created. It is not proven that the whole 0x080702DC class is only a CAN manager.

### Object 0x2002466C
Literal at 0x080019E0, 0x0800BAA4, 0x0803C248, 0x08063D1C, 0x0806E60C.
0x08063D1C leads to code around 0x08063C6C and BL 0x08062A90. 0x0806E60C is used by FUN_0806E59C to read +9/+0xA.

**[OPEN]** full meaning/initialization.

## 11. ETAP21–38 artefact map

ETAP21: resource_table_full.csv, write_callers_raw.txt, can_handlers_and_vtables.txt, 12-handler RAW.  
ETAP22: ETAP22_RAW_DUMP.zip, resource_table_188_clean.csv, write_and_init_windows.txt, can_blx_indirect_scan.txt.  
ETAP23: ETAP23_RAW_DUMP.zip, parameter TX engine, init 0x0800FF44, CAN BLX targets; MOVW hits for 0x0584/0x0604.  
ETAP24: ETAP24_RAW_DUMP.zip, caller/init windows, CAN windows, resource summary; 21 UI resource-ID candidates.  
ETAP25: ETAP25_RAW_DUMP.zip, protocol constants, subtables/init pool.  
ETAP26: ETAP26_RAW_DUMP.zip, UI/parameter BLX scan; 655 BLX hits in requested area.  
ETAP27: ETAP27_RAW_DUMP.zip, UI resource literals/builders; 0 requested full-address hits.  
ETAP28: ETAP28_RAW_DUMP.zip, full-bin literals/subtables; 0 requested full-address hits.  
ETAP29: ETAP29_RAW_DUMP.zip, low16 hits; 8 hits.  
ETAP30: ETAP30_RAW_DUMP.zip, esp32_resources_188.json.  
ETAP31–32: P0 TX-chain RAW.  
ETAP33: P1 RX-family RAW.  
ETAP34: P2 frame/parameter windows.  
ETAP35: P3 local parameter-write windows.  
ETAP36: P4 selected resource records/subtables.  
ETAP37: P5 UI-build area.  
ETAP38: P6 parameter/frame tail windows.

## 12. Live CAN validation plan

1. ESP32-C6 + CAN transceiver in passive listen-only mode.
2. Log timestamp, StdId/ExtId, DLC, Data[0..7], direction/channel.
3. Preserve raw log before normalization.
4. Correlate frames with deliberate actions on the original controller.
5. Do not transmit until the target path is identified.

Priority:
1. passively identify 0x0604 and 0x0584;
2. correlate READ/WRITE/RESPONSE/ACK/ERROR;
3. verify index/subindex;
4. verify types 1..5;
5. correlate value changes with local parameter storage;
6. only then perform controlled TX tests.

A protocol fact should be marked confirmed only when ID, DLC, command, index/subindex, type, value, response and device/local effect agree and a RAW record is preserved.

## 13. ESP32-C6 + Home Assistant architecture

```
Home Assistant
      │
ESP32-C6 HA adapter / entity generator
      │
Estyma protocol layer
(dispatch / state / params / validation / responses)
      │
CAN driver / Estyma frame layer
(RX queue / TX queue / trace)
      │
CAN transceiver
      │
Estyma CAN bus
```

Suggested source tree:
```
src/can/
src/protocol/
src/parameters/
src/resources/
src/homeassistant/
src/diagnostics/
```

Core principle: reproduce observable protocol/behavior, not necessarily Estyma's internal FreeRTOS architecture.

## 14. Next priorities

1. OPEN-1 / P0: solve the exact TX adapter chain.
2. OPEN-2 / P1: classify remaining RX families.
3. OPEN-3 / P2: build the evidence-backed CAN catalogue.
4. OPEN-4 / P3: close UI/local write → CAN TX.
5. OPEN-5 / P4/P5: resource ↔ parameter ↔ CAN ↔ RAM and UI mapping.
6. OPEN-7: finish resource/widget/TypedText/Bitmap/callback.
7. OPEN-6: separately resolve 0x20005EF0..0x20005F5B.

## 15. Final status after ETAP38

**Hard/confirmed:** firmware identity, CAN2, RX/TX queues, 20-byte EstymaCanFrame, RX dispatcher, parameter lookup/write engine, types 1..5, 188 resource records, TypedText base 0x5BE64, principal 0x0604/0x0584 paths, vtable 0x08094508 slot 5/8, 0x080629FC poll path, 0x0806E59C TX queue wrapper, 0x0800FF50 parameter receiver/response construction, and the 11 additional RX handler entry families.

**Still open:** exact TX BLX target from 0x200114C0, full UI → CAN TX bridge, semantics of remaining RX handlers, complete CAN catalogue, parameter ↔ CAN mapping, full resource/widget mapping, 0x20005EF0..0x20005F5B, and live-bus validation.

## 16. Rule for the next agent/chat

Do not restart the RE. Read this document and the ETAP1–30 master first. Prefer existing RAW dumps before whole-BIN scans. Never close an OPEN without direct BIN evidence or controlled live-CAN evidence. Never restore a REJECTED hypothesis without new evidence. Keep RAW and interpretation separate.

**Main unresolved chain:**
`0x200114C0 → [obj+0] → vptr → vtable slot 0 → BLX target → TX adapter → CanMessagesToTransmit → CanTxTask → FUN_08061734 → CAN2`

Until this chain is solved, the main TX architecture is not 1:1 closed.
