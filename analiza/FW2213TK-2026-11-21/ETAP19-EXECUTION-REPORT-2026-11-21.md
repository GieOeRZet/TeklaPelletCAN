# TEKLAPELLET-CAN — ETAP 19 EXECUTION REPORT
**Data:** 2026-11-21  
**Firmware:** `FW2213TK_kopia.bin`  
**SHA-256:** `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`  
**BIN:** `0x1F0000` B = `2 031 616` B  
**Branch:** `ccr-be8a1bcb-5t76j0`

## Executive result

Etap 19 was executed directly against the physical BIN.

The requested searches produced three important results:

1. **`0x2002466C` has exactly 5 byte-level occurrences in the BIN, but only 2 are actual code literal-pool references.**
   - `0x08063D1C` is loaded by `0x08063C6C` and passed as the object/context pointer to the RX handler `0x08062A90`.
   - `0x0806E60C` is loaded by `0x0806E59C` and used as the TX-adapter state/config object.
   - The other three occurrences (`0x080019E0`, `0x0800BAA4`, `0x0803C248`) are embedded byte sequences in code/data regions and do not form executable literal-pool references to the object.
   - No direct BIN reference was found that writes a vtable/object pointer specifically into `[0x2002466C+0x14]`.
   - Therefore the exact initialization of field `+0x14` remains **[OPEN]**.

2. **All direct callers of constructor `0x080157A0` were found:**
   - `0x0800F2BE` with `r0 = r4 + 0xD0`
   - `0x0800FD8A` with `r0 = r4 + 0x24`
   - `0x0800FDB2` with `r0 = r4 + 0x24`
   - `0x0800FDBA` with `r0 = r4 + 0x3C`
   - `0x080702F6` with `r0 = r4 + 0x30`

   None directly passes literal `0x2002466C`. The constructor itself sets `[object+0] = 0x080A4508`, i.e. the dispatch table physically located at `0x08094508`.

3. **The requested TX-write search did not reveal a second CAN-frame constructor in the `0x08062900..0x080629FB` region or in the three requested dispatch slots.**
   - `EstymaTask @ 0x08062C94` does **not** call `0x080629FC`.
   - It runs a periodic/application loop and calls unrelated timer/state/helper routines.
   - Slot 9 `0x08063798` is a calculation/state-update routine; no CAN-frame construction or queue send.
   - Slot 12 `0x08063FD0` is an RX/state handler; it parses `base+0x180/+0x280` and writes object fields, not TX.
   - Slot 0 `0x0805967C` is an object/state routine with an indirect callback; no CAN queue send or CAN frame constructor.
   - The `0x08062900..0x080629FB` area contains a mathematical helper at `0x08062920` and ends immediately before the already-known poller `0x080629FC`. No `0x0604`, `0x22`, `0x23`, `0x2B`, or `0x2F` frame construction was found there.

A major new hard fact is in the requested ACK/SDO candidates:

- `0x0800FF50` receives `StdId = object+0x08 + 0x600`, accepts `(data[3] >> 5) == 1` or `2`, extracts parameter index from `data[4..5]`, type from `data[6]`, decodes values from `data[7..10]`, and calls `0x08011812` to update the local parameter storage. It then prepares a response-like frame with `StdId = object+0x08 + 0x580`, command byte `0x80`, parameter index/type/status fields, and dispatches it through the object's vtable.
- `0x0806369E` receives `StdId = object+0x14 + 0x584` with `(data[3] >> 5) == 2`, requires `data[4..5] == 0x2001`, optionally requires `data[6] == 1`, and stores the 16-bit value from `data[7..8]` into object `+0x10`. Its alternate `+0x1EE` branch stores two 16-bit values from `data[3..6]` into object `+0x16` and `+0x18`.
- These functions are **strongly consistent with parameter protocol/response handling**, but the report does not label them "CANopen SDO ACK" as a hard fact because the firmware itself does not contain that semantic name.

---

# RAW EXPORT

## P1.1 — All byte-level occurrences of `0x2002466C`

Pattern: `6C 46 02 20`

| Address | Classification |
|---|---|
| `0x080019E0` | `[REJECTED]` as object reference; embedded bytes in code/data area |
| `0x0800BAA4` | `[REJECTED]` as object reference; embedded bytes in code/data area |
| `0x0803C248` | `[REJECTED]` as object reference; embedded bytes in code/data area |
| `0x08063D1C` | `[NEW-HARD]` literal pool used by `0x08063C6C` |
| `0x0806E60C` | `[NEW-HARD]` literal pool used by `0x0806E59C` |

### `0x08063C6C` → `0x08063D1C`

Relevant code:

```text
08063C64: 482c          ldr r0, [pc, #0xb0]   ; 0x08063D18
08063C66: f7ab fa33     bl  0x0800F0D0

08063C6A: 4669          mov r1, sp
08063C6C: 482b          ldr r0, [pc, #0xac]   ; 0x08063D1C
08063C6E: f7fe ff0f     bl  0x08062A90
```

Literal:

```text
08063D1C: 6C 46 02 20   = 0x2002466C
```

Therefore `0x08062A90` is explicitly invoked with `r0 = 0x2002466C` from this fan-out path.

This is the strongest direct proof that the object/context used by `0x08062A90` is the global structure at `0x2002466C`.

### `0x0806E59C` → `0x0806E60C`

Relevant code:

```text
0806E5E2: 480a          ldr  r0, [pc, #0x28]  ; 0x0806E60C
0806E5E4: 7A42          ldrb r2, [r0, #0x9]
0806E5E6: 2A00          cmp  r2, #0
0806E5E8: BF04          itt  eq
0806E5EA: 7A80          ldrbeq r0, [r0, #0xa]
0806E5EC: 2801          cmpeq r0, #1
...
0806E60C: 6C 46 02 20   = 0x2002466C
```

The TX adapter therefore directly reads:

- `[0x2002466C + 0x09]`
- `[0x2002466C + 0x0A]`

before deciding whether a `0x0604` frame should enter `CanMessagesToTransmit`.

### Important limitation

There is no additional executable literal reference to `0x2002466C` that directly writes:

```c
*(uint32_t *)(0x2002466C + 0x14) = ...
```

and no literal `0x2002466C` was found at the known constructor callers.

Therefore:

**`[0x2002466C+0x14]` exact initialization remains `[OPEN]`.**

---

## P1.2 — Constructor `0x080157A0`

Constructor:

```text
080157A0: b510          push {r4, lr}
080157A2: 4604          mov  r4, r0
080157A4: 211e          movs r1, #0x1e
080157A6: f7ff f83d     bl   0x08014824
080157AA: 4802          ldr  r0, [pc, #0x8]   ; 0x080157B4
080157AC: 6020          str  r0, [r4]
080157AE: 4620          mov  r0, r4
080157B0: bd10          pop  {r4, pc}

080157B4: 0x080A4508
```

Translation:

```text
0x080A4508 -> physical dispatch table 0x08094508
```

### Direct callers

Whole-BIN direct branch scan:

| Caller | Instruction | Object passed to constructor |
|---|---|---|
| `0x0800F2BE` | `BL 0x080157A0` | `r4 + 0xD0` |
| `0x0800FD8A` | `BL 0x080157A0` | `r4 + 0x24` |
| `0x0800FDB2` | `BL 0x080157A0` | `r4 + 0x24` |
| `0x0800FDBA` | `BL 0x080157A0` | `r4 + 0x3C` |
| `0x080702F6` | `BL 0x080157A0` | `r4 + 0x30` |

No direct caller passes the literal `0x2002466C`.

### Interpretation

`0x080157A0` definitely constructs objects whose first word is the vtable/dispatch table `0x08094508`.

It is **not proven** that any one of the five constructor call sites initializes the object currently referenced through `[r4+0x14]` in `0x08062AE4`.

---

# P2 — TX WRITE SEARCH

## P2.1 — `EstymaTask @ 0x08062C94`

Raw Thumb disassembly:

```text
08062C94: e92d 4ff0     push.w {r4,r5,r6,r7,r8,r9,r10,r11,lr}
08062C98: 4d79          ldr   r5,[pc,#0x1e4]      ; 0x200248E6
08062C9A: f8df 91e8     ldr.w r9,[pc,#0x1e8]      ; 0x20024730
08062C9E: 7828          ldrb  r0,[r5]
08062CA0: b083          sub   sp,#0xc
08062CA2: b920          cbnz  r0,0x62cae
08062CA4: 2001          movs  r0,#1
08062CA6: 7028          strb  r0,[r5]
08062CA8: 4648          mov   r0,r9
08062CAA: f000 f9f4     bl    0x63096
08062CAE: 4648          mov   r0,r9
08062CB0: f000 fa5d     bl    0x6316e
08062CB4: f7f4 fe4d     bl    0x57952
08062CB8: 9000          str   r0,[sp]
08062CBA: f241 7870     movw  r8,#0x1770
08062CBE: f8df b1c8     ldr.w r11,[pc,#0x1c8]    ; 0x20024820
08062CC2: 4f72          ldr   r7,[pc,#0x1c8]     ; 0xC00BF500
08062CC4: 4c72          ldr   r4,[pc,#0x1c8]     ; 0x20024874
08062CC6: f8df a1cc     ldr.w r10,[pc,#0x1cc]    ; 0x200248E7
08062CCA: 4e73          ldr   r6,[pc,#0x1cc]     ; 0x200243E4
...
08062CCE..08062D80:
    periodic state/timer calculations,
    calls 0x080630D4, 0x08062F18,
    0x080577C2, 0x0800D92C,
    0x080631A8, 0x080631AA,
    0x08003921C and 0x080060518,
    updates counters/state,
    and loops.
```

Important direct-call set visible in this task:

- `0x08063096`
- `0x0806316E`
- `0x08057952`
- `0x080630D4`
- `0x08062F18`
- `0x080577C2`
- `0x0800D92C`
- `0x080631A8`
- `0x080631AA`
- `0x08003921C`
- `0x080060518`

There is **no call to `0x080629FC`** and no direct call to `0x0806E59C` in the shown main loop.

Therefore:

**`EstymaTask` is not the direct caller of the already-known parameter-read poller `0x080629FC`.**

---

## P2.2 — Slot 9: `0x08063798`

The slot starts:

```text
08063798: b5f8          push {r3,r4,r5,r6,r7,lr}
0806379A: 4604          mov  r4,r0
0806379C: f000 f87c     bl   0x08063898
080637A0: f104 034c     add.w r3,r4,#0x4c
080637A4: f104 0020     add.w r0,r4,#0x20
...
08063854: f9b0 5020     ldrsh.w r5,[r0,#0x20]
08063858: 42a9          cmp   r1,r5
...
08063864: 4351          muls  r1,r2,r1
08063866: 885a          ldrh  r2,[r3,#0x2]
08063868: 4b0a          ldr   r3,[pc,#0x28]
08063874: fbe1 3203     umlal r3,r2,r1,r3
08063878: 0a11          lsrs  r1,r2,#0x8
0806387E: 8501          strh  r1,[r0,#0x28]
08063880: 7841          ldrb  r1,[r0,#0x1]
08063882: f104 0024     add.w r0,r4,#0x24
08063886: f7f5 ff1e     bl   0x080596C6
...
08063892: e081          b     0x08063998
```

No CAN frame construction, no `0x08057224`, no `0x0604`, and no parameter-write command construction.

**Status: `[NEW-HARD]` slot 9 is not the missing TX-write builder.**

---

## P2.3 — Slot 12: `0x08063FD0`

```text
08063FD0: 490c          ldr   r1,[pc,#0x30]
08063FD2: 8809          ldrh  r1,[r1]
08063FD4: f64c 43cd     movw  r3,#0xcccd
...
08063FE4: d10d          bne   0x08064002

08063FE6: f890 1020     ldrb.w r1,[r0,#0x20]
08063FEA: 291e          cmp   r1,#0x1e
08063FEC: da01          bge   0x08063FF2
08063FEE: 1c49          adds  r1,#1
08063FF0: e044          b     0x0806407C

08063FF2: 2100          movs  r1,#0
08063FF4: 7301          strb  r1,[r0,#0xc]
08063FF6: 7341          strb  r1,[r0,#0xd]
08063FF8: 74c1          strb  r1,[r0,#0x13]
08063FFA: 7501          strb  r1,[r0,#0x14]
08063FFC: 7381          strb  r1,[r0,#0xe]
08063FFE: 6181          str   r1,[r0,#0x18]
08064000: 61c1          str   r1,[r0,#0x1c]
08064002: 4770          bx    lr
```

The continuation at `0x08064008` parses:

- `StdId == base+0x180`: `data[3]&0x7F`, and four 2-bit fields from `data[4]`.
- `StdId == base+0x280`: `data[3]&0x0F`, `data[3]>>4`, 32-bit value from `data[4..7]`, and 32-bit value from `data[8..10]`.

It writes those values into object offsets `+0x0C`, `+0x0D`, `+0x0E`, `+0x13`, `+0x14`, `+0x18`, `+0x1C`, `+0x20`.

No TX queue operation.

**Status: `[NEW-HARD]` slot 12 is an RX/state parser, not the missing TX-write builder.**

---

## P2.4 — Slot 0: `0x0805967C`

```text
0805967C: b510          push {r4,lr}
0805967E: 4604          mov  r4,r0
08059680: 68a0          ldr  r0,[r4,#0x8]
08059682: b1d8          cbz   r0,0x596BC
...
080596B2: 6802          ldr  r2,[r0]
080596B4: 8941          ldrh r1,[r0,#0xA]
080596B6: 6892          ldr  r2,[r2,#0x8]
080596B8: 4790          blx  r2
...
080596D6: 7d41          ldrb r1,[r0,#0x15]
080596D8: 7982          ldrb r2,[r0,#0x6]
...
08059706: 7541          strb r1,[r0,#0x15]
08059708: 4770          bx   lr
```

This is object/state logic with an indirect callback. No `CanMessagesToTransmit`, no `0x08057224`, no CAN frame construction.

**Status: `[NEW-HARD]` slot 0 is not the missing TX-write builder.**

---

## P2.5 — `0x08062900..0x080629FB`

The executable area immediately before the poller contains:

- `0x08062920` — mathematical/calculation routine.
- It performs signed division/multiplication and calls `0x0803BBF4`, `0x0803BC3C`, `0x0803BB58`.
- It returns a calculated 64-bit-ish result.
- It does **not** build an Estyma CAN frame.
- It does **not** reference `0x08057224`.
- It does **not** contain `movw #0x0604`.
- It does **not** contain the requested write command constants `0x22`, `0x23`, `0x2B`, `0x2F` in a frame-building context.

The next executable function starts at:

```text
0x080629FC
```

which is the already-known parameter-read poller.

**Status: `[REJECTED]` as location of the missing TX-write builder.**

---

# P3 — ACK / SDO CANDIDATES

## P3.1 — `0x0800FF50`

Filter:

```text
0800FF50: 8903          ldrh r3,[r0,#0x8]
0800FF52: 880a          ldrh r2,[r1]
0800FF54: f503 63c0     add.w r3,r3,#0x600
0800FF58: 429a          cmp  r2,r3
0800FF5A: d104          bne  0xFF66

0800FF5C: 78ca          ldrb r2,[r1,#0x3]
0800FF5E: 0952          lsrs r2,r2,#0x5
0800FF60: 2a01          cmp  r2,#1
0800FF62: d101          bne  0xFF68
...
0800FF68: 2a02          cmp  r2,#2
0800FF6A: d1fc          bne  0xFF66
```

Thus it accepts:

```text
StdId = object+0x08+0x600
(data[3] >> 5) == 1 OR 2
```

Then:

- `data[4..5]` → 16-bit parameter index `r8`.
- `data[6]` → type selector `r5`.
- parameter record lookup: `0x080115F6`.
- type lookup: `0x08010FC2`.

For `r5 == 1`, value is `data[7]`.

For `r5 == 2`, value is little-endian `data[7..8]`.

For `r5 == 3`, value is little-endian 32-bit `data[7..10]`.

For `r5 == 4`, value is little-endian signed 16-bit `data[7..8]`.

For `r5 == 5`, value is little-endian 32-bit `data[7..10]`.

Then:

```text
08010040: ... 
08010044: 6860          ldr r0,[r4,#0x4]
08010046: 4641          mov r1,r8
08010048: f001 fbe3     bl  0x08011812
```

So the received message causes a local parameter update through `0x08011812`.

### Response construction

The handler initially prepares:

```text
sp+0x08 = object+0x08+0x580
sp+0x0A = 0x08
sp+0x0B = 0x80
sp+0x0C..0x0D = received parameter index
sp+0x0E = received type
```

After `0x08011812`, it maps the result/status into:

```text
sp+0x0F
sp+0x10
sp+0x11
sp+0x12
```

and dispatches the prepared frame through:

```text
[r4] -> vtable -> second-level method
```

at `0x080100BE..0x080100C6`.

### Hard conclusion

`0x0800FF50` is a **parameter-message receiver + local parameter write + response generation**.

It is highly consistent with a request/response protocol.

However:

**`[OPEN]`** whether this is specifically CANopen SDO `0x600/0x580` semantics is not proven by firmware naming alone. The numeric `+0x600/+0x580`, parameter index, type/value and response behavior are hard facts; the CANopen label is interpretation.

---

## P3.2 — `0x0806369E`

Exact relevant code:

```text
0806369E: b510          push {r4,lr}
080636A0: 4604          mov  r4,r0
080636A2: 7d20          ldrb r0,[r4,#0x14]
080636A4: 880a          ldrh r2,[r1]
080636A6: f200 5384     addw r3,r0,#0x584
080636AA: 429a          cmp r2,r3
080636AC: d116          bne 0x636DC

080636AE: 78c8          ldrb r0,[r1,#0x3]
080636B0: 0940          lsrs r0,r0,#0x5
080636B2: 2802          cmp r0,#2
080636B4: d111          bne 0x636DA

080636B6: 2000          movs r0,#0
080636B8: 74e0          strb r0,[r4,#0x13]

080636BA: 790a          ldrb r2,[r1,#0x4]
080636BC: 7948          ldrb r0,[r1,#0x5]
080636C2: f242 0201     movw r2,#0x2001
080636C6: 4290          cmp r0,r2
080636C8: bf04          itt eq
080636CA: 7988          ldrbeq r0,[r1,#0x6]
080636CC: 2801          cmpeq r0,#1
080636CE: d104          bne 0x636DA

080636D0: 7a08          ldrb r0,[r1,#0x8]
080636D2: 79c9          ldrb r1,[r1,#0x7]
080636D4: ea41 2000     orr.w r0,r1,r0,lsl #8
080636D8: 8220          strh r0,[r4,#0x10]
```

Hard fields:

- ID: `base + 0x584`, where base is `[object+0x14]`.
- command/type discriminator: `(data[3] >> 5) == 2`.
- `data[4..5] == 0x2001`.
- `data[6] == 1`.
- value: little-endian `data[7..8]`.
- destination: `object+0x10`.
- side effect: `object+0x13 = 0`.

Alternate branch:

```text
StdId == base+0x1EE
```

then:

- `data[3..4]` → object `+0x16`
- `data[5..6]` → object `+0x18`

No TX queue call.

### Hard conclusion

`0x0806369E` is a **specific RX response/state handler**.

It can plausibly participate in an acknowledgement/response path because it consumes a narrowly filtered frame and stores returned data, but the firmware does not itself establish the semantic name "SDO ACK".

---

# XREF / CALLGRAPH

## Confirmed RX side

```text
CAN2 RX
  |
  v
FUN_080617DC
  |
  v
ReceivedCanMessages
  |
  v
CanRxTask
  |
  v
FUN_08063B80
  |
  +--> 0x0800FF50
  |      |
  |      +--> parameter lookup
  |      +--> 0x08011812
  |      +--> response-like 0x580 frame via vtable
  |
  +--> 0x0806369E
  |      |
  |      +--> base+0x584 / 0x1EE
  |      +--> object state
  |
  +--> 0x08062A90
         |
         +--> 0x08062B22
                |
                +--> 0x08011812
                |
                +--> local parameter RAM
```

## Confirmed parameter-read TX side

```text
0x080629FC
  |
  | table + counter*0x2C + 0x08
  v
parameter index
  |
  v
0x08062AE4
  |
  | StdId = 0x0604
  | data[2] = 0x08
  | data[3] = 0x40
  | data[4..5] = parameter index
  | data[6] = 0x01
  v
[r4+0x14] -> indirect vtable call
  |
  v
0x0806E59C
  |
  v
0x08057224
  |
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
CAN2
```

## Missing TX-write path

Still not closed:

```text
UI parameter change
       |
       v
local parameter storage
       |
       ????????????????????
       |
       v
CAN TX frame
```

The requested Etap 19 candidates do not close this path.

---

# INTERPRETACJA

## 1. `0x2002466C` is definitely a shared CAN/application context

The same global structure is passed into the RX handler fan-out and read by the `0x0604` TX adapter.

This is hard evidence.

What is **not** hard yet is the origin of its `+0x14` field.

## 2. The vtable `0x08094508` is real, but the exact instance remains open

`0x080157A0` proves the table is used as an object dispatch table.

Its callers construct nested objects at offsets:

- `+0xD0`
- `+0x24`
- `+0x24`
- `+0x3C`
- `+0x30`

None of these direct calls proves that the constructed object is the exact object stored at `0x2002466C+0x14`.

## 3. `EstymaTask` is not the obvious TX-write engine

The main loop does not call `0x080629FC`.

It performs periodic calculations/state updates and calls helper functions.

Therefore the missing parameter-write TX path is likely:
- another application/UI callback,
- an indirect vtable call,
- another task/context,
- or a data-driven path not represented by a second literal `0x0604`.

## 4. `0x0800FF50` is the strongest new protocol clue

It has the exact structure expected from a parameter request/response mechanism:

```text
RX ID = base + 0x600
       |
       +--> parameter index
       +--> type
       +--> value
       |
       v
local parameter write
       |
       v
response ID = base + 0x580
```

This is much stronger evidence for a parameter protocol than the previously inspected generic handlers.

Still, the semantic name **SDO** remains `[OPEN]` until another independent firmware path or external CAN trace confirms it.

## 5. `0x0806369E` looks like a response/state consumer

Its `base+0x584`, `0x2001`, type `1`, and 16-bit returned value are highly structured.

It does not transmit anything itself.

---

# STATUS

| Item | Status | Result |
|---|---|---|
| All `0x2002466C` byte occurrences | **[NEW-HARD]** | 5 total |
| Actual executable literal refs to `0x2002466C` | **[NEW-HARD]** | `0x08063D1C`, `0x0806E60C` |
| Other 3 occurrences as object refs | **[REJECTED]** | embedded/non-reference byte sequences |
| `0x2002466C` passed to `0x08062A90` | **[NEW-HARD]** | yes, via `0x08063C6C` |
| `0x2002466C` used by `0x0806E59C` | **[NEW-HARD]** | yes |
| Exact `[0x2002466C+0x14]` initialization | **[OPEN]** | no direct assignment found |
| Exact `[0x2002466C+0x18]` origin | **[OPEN]** | object is consumed as context; initializer not found |
| Direct callers `0x080157A0` | **[NEW-HARD]** | 5 callers |
| Constructor sets vtable `0x08094508` | **[CONFIRMED-REPEAT]** | yes |
| Any direct constructor caller passing `0x2002466C` | **[REJECTED]** | none |
| `EstymaTask -> 0x080629FC` | **[REJECTED]** | no direct call |
| Slot 9 `0x08063798` = TX builder | **[REJECTED]** | no CAN TX construction |
| Slot 12 `0x08063FD0` = TX builder | **[REJECTED]** | RX/state parser |
| Slot 0 `0x0805967C` = TX builder | **[REJECTED]** | state/callback logic |
| `0x62900..0x629FB` = TX builder | **[REJECTED]** | calculation/helper area |
| `0x0800FF50` parameter RX/write | **[NEW-HARD]** | yes |
| `0x0800FF50` response-like `+0x580` frame | **[NEW-HARD]** | yes |
| `0x0800FF50` = CANopen SDO handler | **[OPEN]** | semantics not named/proven by firmware |
| `0x0806369E` structured RX response/state handler | **[NEW-HARD]** | yes |
| `0x0806369E` = SDO ACK specifically | **[OPEN]** | plausible, not proven |
| Missing UI→CAN parameter TX write path | **[OPEN]** | not closed in Etap 19 |
| SRAM `0x20005EF0..0x20005F5B` | **[OPEN]** | unchanged |

## Highest-value next target

The strongest remaining branch is now:

**`0x0800FF50` response generation → its indirect vtable target → actual TX dispatch path.**

That path may expose the missing **UI/parameter-write CAN TX mechanism** without guessing from CAN IDs.