# AUTONOMOUS 10-PASS REPORT 08 — CAN READ/TX OBJECT GRAPH
Date: 2026-11-22
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Executive
This pass was a 10-pass cross-check of the existing RAW-derived CAN read/TX graph. It did not invent a new D60 vptr. The strongest result is a clean separation of two object roles:

- 0x2002466C is HARD-confirmed as the object whose vptr is 0x080A4568 and whose slot 0 is 0x080629FC (cyclic parameter-read poller).
- 0x08062AE4 constructs the 0x0604/0x40 READ frame and dispatches through the *separate* object pointer at [poller+0x14].
- Physical dispatch table 0x08094508 is HARD-confirmed to contain 0x0806E59C at slot 5 and 0x080629FC at slot 8, and constructor 0x080157A0 installs that table.
- 0x0806E59C is HARD-confirmed to queue the 0x0604 frame through 0x200244EC -> 0x08057224.
- The exact assignment of the READ object's +0x14 to the slot-5 class remains OPEN.
- D60 remains OPEN; prior overstatement is explicitly rejected.

## Ten passes

### Pass 1 — poller object
HARD: constructor 0x080103EC for RAM 0x2002466C installs vtable 0x080A4568.
HARD: slot 0 = 0x080629FC.

### Pass 2 — poller state
HARD: 0x080629FC sets object+0x0A to 1 when 0x08062C78 >= 0x1F.
HARD: it derives parameter ID from runtime table base object+0x18, counter*0x2C, +0x08.

### Pass 3 — READ frame producer
HARD: 0x08062AE4 builds DLC 8, command 0x40, parameter index bytes, type 1, StdId 0x0604.

### Pass 4 — indirect boundary
HARD: 0x08062AE4 does not BL 0x0806E59C; it BLX through [object+0x14], then vtable slot 0.
This is a real object boundary, not a guessed direct call.

### Pass 5 — physical dispatch table
HARD: physical table 0x08094508 contains slot 5 -> 0x0806E59C and slot 8 -> 0x080629FC.
HARD: 0x080157A0 installs high-space 0x080A4508 (same physical table).

### Pass 6 — TX adapter
HARD: 0x0806E59C requires input ID 0x0604, copies the frame into a local 0x14-byte buffer, and uses 0x200244EC as TX queue handle.

### Pass 7 — queue transport
HARD: 0x08057224 is queue-send primitive; CAN-region caller is 0x0806E604 from 0x0806E59C.
Transport is separated from application frame construction.

### Pass 8 — RX parameter write
HARD: 0x08062A90 -> 0x08062B22 -> 0x08011812 for the 0x0584 branch with data[3]>>5 == 2.
This is independent of the READ TX producer.

### Pass 9 — UI/text cross-check
HARD: existing Heating TypedText mappings remain consistent; no evidence found that would collapse TypedText IDs into bitmap IDs or CAN IDs.

### Pass 10 — D60 source discipline
HARD correction: direct whole-BIN literal counts are 0 for 0x20008D60 and 0x080A4544. Therefore D60 vptr and slot-0 target remain OPEN. No promotion.

## Net result

### Newly strengthened / closed
1. Two-object separation in the 0x0604 READ path.
2. Physical dispatch table identity shared by poller and TX adapter.
3. Transport boundary 0x0806E59C -> 0x08057224.
4. Explicit rejection of a direct 0x62AE4 -> 0x6E59C call.

### Still OPEN
- exact object stored at [poller+0x14];
- exact write of [0x20008D60];
- concrete slot-0 target for that object;
- full UI local-write -> outbound CAN bridge;
- complete handler map and protocol semantics.

## Progress assessment
The previous project-level heuristic estimate was ~55–60%. This pass does NOT justify a large percentage jump because several closures are refinements of already-known edges.

Recommended current heuristic:
**~57–61% functional reverse-engineering closure**, i.e. approximately **+1 to +2 percentage points** versus the previous estimate.

This is not a formal mathematical metric. It is a coverage estimate of firmware behavior needed for a software-first 1:1 reconstruction.

## Next target
Recover the concrete initializer/object graph for [0x2002466C+0x14], then trace that object to its vptr and slot 0. In parallel, continue D60 write-source recovery.
