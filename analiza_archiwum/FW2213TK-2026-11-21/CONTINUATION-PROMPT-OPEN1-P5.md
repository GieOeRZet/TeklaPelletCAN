# TEKLAPELLET-CAN / NewEstymaCan — CONTINUATION OPEN1-P5

Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

## Source of truth
Work directly on:
- FW2213TK_kopia.bin
- size 0x1F0000
- SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

**Do not use RE_PACK as a source of bytes.** RE_PACK addresses may be mentioned only as auxiliary mapping. Critical evidence must come from the canonical BIN.

## Read first
1. analiza_archiwum/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-52-FINAL.md
2. analiza_archiwum/FW2213TK-2026-11-21/RAW_PACKET7_OPEN1_P4.txt

## Current confirmed chain
0x200114C0
 -> [obj+0] = 0x20008D60
 -> [0x20008D60]
 -> [vtable]
 -> slot 0
 -> BLX

Confirmed separately:
- FUN_0806E59C is a TX wrapper using queue 0x200244EC -> 0x08057224 -> CanTxTask -> FUN_08061734 -> CAN2.
- vtable 0x080A4568 belongs to object 0x2002466C and slot 0 is 0x080629FC.
- 0x080629FC sets object +0x0A to 1 at 0x08062A86 when 0x08062C78 >= 0x1F.
- CAN2_RX0 vector -> 0x0806F9F8 -> 0x080617DC -> RX queue -> 0x08063B80.

## PRIMARY TASK — CLOSE OPEN-1
Find the first real runtime write to:
    [0x20008D60]

Then prove:
1. exact value written;
2. whether it is a vtable/interface pointer;
3. complete vtable/interface contents around slot 0;
4. exact slot-0 target;
5. whether target is FUN_0806E59C, another wrapper, or something else;
6. complete path from that target to 0x200244EC / CanTxTask / FUN_08061734 / CAN2.

## Required methodology
- Search all instruction patterns capable of writing to D60, not only literal LE32 occurrences.
- Follow computed address construction from 0x20008CD0 + 0x90.
- Inspect constructors/functions around 0x0800D9AC, 0x0800DB08, 0x0800DC44 and their callees.
- Inspect startup/init chains, but do not assume every copy loop is .data/.bss.
- If a candidate vtable is found, verify its bytes and target functions directly from BIN.
- Distinguish HARD / STRONG / OPEN / REJECTED.

## Secondary task
If OPEN-1 is closed, independently map the next one-level dependencies needed to establish the TX adapter. Do not restart the whole project or redo unrelated UI/resource analysis.

## Output
Produce one RAW evidence file named:
RAW_PACKET8_OPEN1_P5.txt

It must contain:
- exact source/hash;
- raw addresses and disassembly/evidence;
- exact writes and values;
- vtable dump if found;
- caller/xref evidence;
- final HARD/STRONG/OPEN verdict;
- remaining next-step targets.

If multiple auxiliary files are genuinely required, package them together; otherwise keep the primary result as one TXT file.
