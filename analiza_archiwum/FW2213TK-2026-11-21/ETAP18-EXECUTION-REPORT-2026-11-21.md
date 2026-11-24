# TEKLAPELLET-CAN — ETAP 18 EXECUTION REPORT
**Data:** 2026-11-21  
**Firmware:** `FW2213TK_kopia.bin`  
**SHA-256:** `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`  
**BIN:** `0x1F0000` B = `2 031 616` B  
**Branch:** `ccr-be8a1bcb-5t76j0`

## Executive result

Etap 18 was executed directly against the physical BIN.

The most important new hard result is that the `+0x10000` pointer trail closes a **vtable-like dispatch table** containing both:
- `0x0807E59D` → physical `0x0806E59C`
- `0x080729FD` → physical `0x080629FC`

The table is physically at `0x08094508`. A constructor at `0x080157A0` loads high-space pointer `0x080A4508` and stores it at `[r4+0]`, proving this table is used as a virtual/dispatch table by at least one class.

However, the BIN does **not yet prove directly** that the specific pointer at `[0x2002466C + 0x14]` is an instance of this exact class. The relevant table relationship is hard; the final object-instance assignment remains `[OPEN]`.

A second major result is that `0x08057224` is a FreeRTOS-style `xQueueGenericSend` implementation: its register/stack argument usage matches `(queue, item, ticks-to-wait, copy-position)`, and it calls `0x080574E4`, which is a `prvCopyDataToQueue`-like routine that updates queue state and message count. Therefore the `0x0806E59C -> 0x08057224` path is a real TX queue insertion path.

Within `0x08060000..0x08070000` there is exactly **one** direct call to `0x08057224`: `0x0806E604`, from `0x0806E59C`. Outside that range there are two additional direct transfers:
- `0x08056A1C -> 0x08057224`
- `0x08056A44 -> 0x08057224` (`B.W`)

No additional `movw rX,#0x0604` was found outside the already known `0x08062B0C` and `0x0806E5F2`.

Finally, `0x080629FC` is a cyclic parameter-read poller. It obtains an index from:
`[object+0x18] + counter*0x2C + 0x08`,
stores it at `[object+0x0E]`, and calls `0x08062AE4`, which creates the `0x0604 / 0x40` read request.

# RAW EXPORT

## P1.1 — Scan for `0x0807E59D`

Pattern: `9D E5 07 08`

Result:

| Physical address | Value | Interpretation |
|---|---:|---|
| `0x08094544` | `0x0807E59D` | high-space pointer to physical `0x0806E59C` |

Count: **1**.

### Surrounding dispatch table

Physical table begins at `0x08094508`.

| slot | physical entry | stored pointer | physical target after `(ptr & ~1)-0x10000` |
|---:|---:|---:|---:|
| 0 | `0x08094508` | `0x0806967D` | `0x0805967C` |
| 1 | `0x08094514` | `0x080A5B39` | `0x08095B38` |
| 2 | `0x08094520` | `0x080A5B39` | `0x08095B38` |
| 3 | `0x0809452C` | `0x080A5B39` | `0x08095B38` |
| 4 | `0x08094538` | `0x080A58D7` | `0x080958D6` |
| **5** | **`0x08094544`** | **`0x0807E59D`** | **`0x0806E59C`** |
| 6 | `0x08094550` | `0x080A5B39` | `0x08095B38` |
| 7 | `0x0809455C` | `0x0801EEC9` | `0x0800EEC8` |
| **8** | **`0x08094568`** | **`0x080729FD`** | **`0x080629FC`** |
| 9 | `0x08094574` | `0x08073799` | `0x08063798` |
| 10 | `0x08094580` | `0x080281ED` | `0x080181EC` |
| 11 | `0x0809458C` | `0x080A5B39` | `0x08095B38` |
| 12 | `0x08094598` | `0x08073FD1` | `0x08063FD0` |
| 13 | `0x080945A4` | `0x0801FEA5` | `0x0800FEA4` |
| 14 | `0x080945B0` | `0x0801DBD3` | `0x0800DBD2` |
| 15 | `0x080945BC` | `0x080A5B39` | `0x08095B38` |
| 16 | `0x080945C8` | `0x0801EE61` | `0x0800EE60` |

The next bytes at `0x080945CC` are executable code, so the table terminates there.

### Proof that the table is used as a class/dispatch table

At `0x080157A0`:

```
080157a0: b510          push {r4, lr}
080157a2: 4604          mov  r4, r0
080157a4: 211e          movs r1, #0x1e
080157a6: f7ff f83d     bl   0x08014824
080157aa: 4802          ldr  r0, [pc, #0x8]   ; 0x080157b4
080157ac: 6020          str  r0, [r4]
080157ae: 4620          mov   r0, r4
080157b0: bd10          pop   {r4, pc}

080157b4: 080a4508      ; literal 0x080A4508
```

`0x080A4508` is the high-space form of physical table address `0x08094508`.

Therefore:

`constructor 0x080157A0 -> [object+0] = 0x080A4508 -> physical table 0x08094508`

### Direct object+0x14 proof status

`0x08062AE4` uses:

```
r0 = [r4 + 0x14]
r2 = [r4 + 0x14]
r2 = [r2]
r2 = [r2]
blx r2
```

So `[r4+0x14]` is definitely a pointer to an object containing a vtable/dispatch pointer.

The BIN scan found the dispatch table containing `0x0806E59C`, but no direct literal occurrence of `0x080A4509`/`0x08094509` proving that this exact table address is written into `[0x2002466C+0x14]`.

**Status:** `[NEW-HARD]` table identity; `[OPEN]` exact assignment of this table instance to `[r4+0x14]`.

## P1.2 — All `movw rX,#0x0604`

Exactly **2** executable hits:

1. `0x08062B0C: 40 F2 04 60 — movw r0,#0x604` inside `0x08062AE4`.
2. `0x0806E5F2: F2 40 61 04 — movw r1,#0x604` inside `0x0806E59C`.

No other `movw rX,#0x0604` occurs in the BIN.

Literal `04 06 00 00`: **0 occurrences**.

Other byte-level `04 06` occurrences were checked in CAN-area contexts and are data/table occurrences, not additional MOVW sender instructions.

## P2.1 — Full `0x08057224`

```
08057224: e92d 41f4     push.w {r2,r4,r5,r6,r7,r8,lr}
08057228: b083          sub   sp,#0xc
0805722a: 4604          mov   r4,r0
0805722c: 4688          mov   r8,r1
0805722e: 461e          mov   r6,r3
08057230: 2700          movs  r7,#0x0
08057232: b914          cbnz  r4,0x0805723a
08057234: f000 ff94     bl    0x08058160
08057238: e7fe          b     0x08057238
0805723a: f1b8 0f00     cmp.w r8,#0
0805723e: d101          bne   0x08057244
08057240: 6c20          ldr   r0,[r4,#0x40]
08057242: b938          cbnz  r0,0x08057254
08057244: 2e02          cmp   r6,#2
08057246: d10d          bne   0x08057264
08057248: 6be0          ldr   r0,[r4,#0x3c]
0805724a: 2801          cmp   r0,#1
0805724c: d00a          beq   0x08057264
0805724e: f000 ff87     bl    0x08058160
08057252: e7fe          b     0x08057252
08057254: f000 ff84     bl    0x08058160
08057258: e7fe          b     0x08057258
0805725a: 4620          mov   r0,r4
0805725c: f000 f98a     bl    0x08057574
08057260: f000 fb26     bl    0x080578B0
08057264: f000 feb0     bl    0x08057FC8
08057268: 6ba0          ldr   r0,[r4,#0x38]
0805726a: 6be1          ldr   r1,[r4,#0x3c]
0805726c: 4288          cmp   r0,r1
0805726e: d301          blo   0x08057274
08057270: 2e02          cmp   r6,#2
08057272: d10f          bne   0x08057294
08057274: 4632          mov   r2,r6
08057276: 4641          mov   r1,r8
08057278: 4620          mov   r0,r4
0805727a: f000 f933     bl    0x080574E4
0805727e: 6a60          ldr   r0,[r4,#0x24]
08057280: b138          cbz   r0,0x08057292
08057282: f104 0024     add.w r0,r4,#0x24
08057286: f000 fc62     bl    0x08057B4E
0805728a: 2801          cmp   r0,#1
0805728c: bf08          it eq
0805728e: f000 fe92     bleq 0x08057FB6
08057292: e044          b     0x0805731e
08057294: 9803          ldr   r0,[sp,#0xc]
08057296: b910          cbnz  r0,0x0805729e
08057298: f000 fea2     bl    0x08057FE0
0805729c: e03d          b     0x0805731a
0805729e: b91f          cbnz  r7,0x080572a8
080572a0: 4668          mov   r0,sp
080572a2: f000 fc80     bl    0x08057BA6
080572a6: 2701          movs  r7,#1
080572a8: f000 fe9a     bl    0x08057FE0
080572ac: f000 fafa     bl    0x080578A4
080572b0: f000 fe8a     bl    0x08057FC8
080572b4: 6c60          ldr   r0,[r4,#0x44]
080572b6: f110 0f01     cmn.w r0,#1
080572ba: bf04          itt eq
080572bc: 2000          moveq r0,#0
080572be: 6460          streq r0,[r4,#0x44]
080572c0: 6ca0          ldr   r0,[r4,#0x48]
080572c2: f110 0f01     cmn.w r0,#1
080572c6: bf04          itt eq
080572c8: 2000          moveq r0,#0
080572ca: 64a0          streq r0,[r4,#0x48]
080572cc: f000 fe88     bl    0x08057FE0
080572d0: a903          add   r1,sp,#0xc
080572d2: 4668          mov   r0,sp
080572d4: f000 fc72     bl    0x08057BBC
080572d8: b9d0          cbnz  r0,0x08057310
080572da: f000 fe75     bl    0x08057FC8
080572de: 6ba0          ldr   r0,[r4,#0x38]
080572e0: 6be1          ldr   r1,[r4,#0x3c]
080572e2: 4288          cmp   r0,r1
080572e4: bf0c          ite eq
080572e6: 2501          moveq r5,#1
080572e8: 2500          movne r5,#0
080572ea: f000 fe79     bl    0x08057FE0
080572ee: 2d00          cmp   r5,#0
080572f0: d0b3          beq   0x0805725a
080572f2: 9903          ldr   r1,[sp,#0xc]
080572f4: f104 0010     add.w r0,r4,#0x10
080572f8: f000 fc0a     bl    0x08057B10
080572fc: 4620          mov   r0,r4
080572fe: f000 f939     bl    0x08057574
08057302: f000 fad5     bl    0x080578B0
08057306: 2800          cmp   r0,#0
08057308: d1ac          bne   0x08057264
0805730a: f000 fe54     bl    0x08057FB6
0805730e: e7a9          b     0x08057264
08057310: 4620          mov   r0,r4
08057312: f000 f92f     bl    0x08057574
08057316: f000 facb     bl    0x080578B0
0805731a: 2000          movs  r0,#0
0805731c: e002          b     0x08057324
0805731e: f000 fe5f     bl    0x08057FE0
08057322: 2001          movs  r0,#1
08057324: b004          add   sp,#0x10
08057326: e8bd 81f0     pop.w {r4,r5,r6,r7,r8,pc}
```

The saved `r2` at `[sp+0xC]`, `r1` item pointer, and `r3` copy-position argument match the FreeRTOS queue-send calling convention.

`0x080574E4` operates on queue fields and increments the queue message count at `[queue+0x38]`, strongly matching `prvCopyDataToQueue`.

**[NEW-HARD]** `0x08057224` is a queue-send implementation / queue-send primitive.

## P2.2 — All direct callers

Whole-BIN direct branch scan:

| caller | instruction | location |
|---|---|---|
| `0x08056A1C` | `BL 0x08057224` | outside CAN region |
| `0x08056A44` | `B.W 0x08057224` | outside CAN region |
| `0x0806E604` | `BL 0x08057224` | inside CAN region |

For `0x08060000..0x08070000`: exactly **1** direct caller, `0x0806E604`.

## P3 — `0x08062A00..0x08062A8F`

```
08062A00: 7a20          ldrb r0,[r4,#0x8]
08062A02: 2801          cmp  r0,#1
08062A04: d103          bne  0x08062A0e
08062A06: 2001          movs r0,#1
08062A08: 72e0          strb r0,[r4,#0xb]
08062A0A: 200a          movs r0,#0xa
08062A0C: 7320          strb r0,[r4,#0xc]
08062A0E: 7ae0          ldrb r0,[r4,#0xb]
08062A10: 2801          cmp  r0,#1
08062A12: d11c          bne  0x08062A4e
08062A14: 7c20          ldrb r0,[r4,#0x10]
08062A16: 2801          cmp  r0,#1
08062A18: d119          bne  0x08062A4e
08062A1A: 481c          ldr  r0,[pc,#0x70]
08062A1C: 8801          ldrh r1,[r0]
08062A1E: 69a0          ldr  r0,[r4,#0x18]
08062A20: f7ae fff6     bl   0x08011A10
08062A24: 81e0          strh r0,[r4,#0xe]
08062A26: 89e0          ldrh r0,[r4,#0xe]
08062A28: 2800          cmp  r0,#0
08062A2A: d107          bne  0x08062A3c
08062A2C: 2000          movs r0,#0
08062A2E: 4917          ldr  r1,[pc,#0x5c]
08062A30: 8008          strh r0,[r1]
08062A32: 2000          movs r0,#0
08062A34: 7220          strb r0,[r4,#0x8]
08062A36: 2000          movs r0,#0
08062A38: 72e0          strb r0,[r4,#0xb]
08062A3A: e008          b    0x08062A4e
08062A3C: 89e1          ldrh r1,[r4,#0xe]
08062A3E: 0020          movs r0,r4
08062A40: f000 f850     bl   0x08062AE4
08062A44: 4811          ldr  r0,[pc,#0x44]
08062A46: 8800          ldrh r0,[r0]
08062A48: 1c40          adds r0,#1
08062A4A: 4910          ldr  r1,[pc,#0x40]
08062A4C: 8008          strh r0,[r1]
08062A4E: 7ae0          ldrb r0,[r4,#0xb]
08062A50: 2800          cmp  r0,#0
08062A52: d108          bne  0x08062A66
08062A54: 7b20          ldrb r0,[r4,#0xc]
08062A56: 2800          cmp  r0,#0
08062A58: d003          beq  0x08062A62
08062A5A: 7b20          ldrb r0,[r4,#0xc]
08062A5C: 1e40          subs r0,#1
08062A5E: 7320          strb r0,[r4,#0xc]
08062A60: e001          b    0x08062A66
08062A62: 2000          movs r0,#0
08062A64: 80e0          strh r0,[r4,#0x6]
08062A66: 0020          movs r0,r4
08062A68: f000 f906     bl   0x08062C78
08062A6C: 8a61          ldrh r1,[r4,#0x12]
08062A6E: 3164          adds r1,#0x64
08062A70: b280          uxth r0,r0
08062A72: 4281          cmp  r1,r0
08062A74: da01          bge  0x08062A7a
08062A76: 2000          movs r0,#0
08062A78: 7260          strb r0,[r4,#0x9]
08062A7A: 0020          movs r0,r4
08062A7C: f000 f8fc     bl   0x08062C78
08062A80: 281f          cmp  r0,#0x1f
08062A82: db01          blt  0x08062A88
08062A84: 2001          movs r0,#1
08062A86: 72a0          strb r0,[r4,#0xa]
08062A88: bd10          pop {r4,pc}
```

Function starts at `0x080629FC`.

`0x08011A10`:

```
08011A10: 222c          movs r2,#0x2c
08011A12: 4351          muls  r1,r2,r1
08011A14: 4408          add   r0,r1
08011A16: 8900          ldrh  r0,[r0,#0x8]
08011A18: 4770          bx    lr
```

Therefore:

```
index = *(uint16_t *)(
    *(uint32_t *)(obj + 0x18)
    + counter * 0x2C
    + 0x08
);
```

The index is stored at `obj+0x0E`. If zero, the global counter is reset and polling is disabled. If nonzero, `0x08062AE4(obj,index)` is called and the counter increments.

# XREF / CALLGRAPH

```
PARAMETER POLLER
0x080629FC
    |
    | parameter index from runtime 0x2C-byte table
    v
0x08062AE4
    |
    | StdId 0x0604
    | command 0x40
    v
INDIRECT DISPATCH
[r4+0x14] -> vtable slot
    |
    v
0x0806E59C
    |
    | 20-byte EstymaCanFrame
    v
0x08057224
    |
    | FreeRTOS queue send
    v
CanMessagesToTransmit
    |
    v
CanTxTask
    |
    v
FUN_08061734
    |
    v
CAN2 0x40006800
```

RX write path remains separate:

```
CAN2 RX
  -> FUN_080617DC
  -> ReceivedCanMessages
  -> CanRxTask
  -> FUN_08063B80
  -> 0x08062A90
  -> StdId 0x0584
  -> 0x08062B22
  -> 0x08011812
  -> local parameter RAM
```

# INTERPRETACJA

1. **`0x08057224` is transport, not application CAN encoding.** The CAN frame is constructed before entering it.
2. **`0x0806E59C` is a specialized `0x0604` TX adapter.**
3. **No second hard-coded `0x0604` constructor** was found through the requested whole-BIN MOVW scan.
4. **`0x080629FC` closes the missing trigger** for `0x08062AE4`: it cycles through a runtime parameter table with `0x2C)-byte entries and reads a u16 parameter ID at `+0x08`.
5. **The vtable trail is substantially stronger:** one physical dispatch table contains both `0x0806E59C` and `0x080629FC`.
6. The exact object instance stored at `[r4+0x14]` remains open.

# STATUS

| Item | Status | Result |
|---|---|---|
| High-space `0x0807E59D` scan | **[NEW-HARD]** | 1 occurrence at `0x08094544` |
| Physical target | **[NEW-HARD]** | `0x0806E59C` |
| Dispatch table | **[NEW-HARD]** | physical `0x08094508` |
| Table slot for `0x0806E59C` | **[NEW-HARD]** | slot 5 / `0x08094544` |
| Table slot for `0x080629FC` | **[NEW-HARD]** | slot 8 / `0x08094568` |
| Constructor using table | **[NEW-HARD]** | `0x080157A0` |
| Exact assignment to `[r4+0x14]` | **[OPEN]** | not directly proven |
| MOVW `#0x0604` scan | **[NEW-HARD]** | exactly 2 executable hits |
| Other direct `0x0604` constructor | **[REJECTED]** | none in requested direct scan |
| Literal `04 06 00 00` | **[NEW-HARD]** | 0 hits |
| `0x08057224` role | **[NEW-HARD]** | FreeRTOS-style queue send primitive |
| CAN-region callers | **[NEW-HARD]** | exactly 1: `0x0806E604` |
| All direct callers | **[NEW-HARD]** | `0x08056A1C`, `0x08056A44`, `0x0806E604` |
| Poller/index source | **[NEW-HARD]** | runtime table `+counter*0x2C+8` |
| Polling interpretation | **[NEW-STRONG]** | cyclic parameter-read scheduler |
| Full UI write-to-CAN path | **[OPEN]** | indirect/data-driven path still unresolved |
| SRAM `0x20005EF0..0x20005F5B` | **[OPEN]** | unchanged |

## Next highest-value target

**Which exact object instance is stored at `[r4+0x14]`, where it is initialized, and how its vtable assignment connects to physical table `0x08094508`.**
