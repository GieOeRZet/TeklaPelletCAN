# TEKLAPELLET-CAN — ETAP 14 — EXECUTION MANIFEST

Data: 2026-11-20
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0
Source: TEKLAPELLET-CAN-ETAP14-WYNIK-2026-11-20.md
BIN: FW2213TK_kopia.bin
BIN SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

ROLE
This file records the execution handoff. The uploaded Etap 14 result is the controlling source for this turn. No independent scope change or speculative closure is authorized.

CONFIRMED NEW-HARD
- Task pointers: DAT_08062EAC -> 0x08062C8B; DAT_08062EB0 -> 0x08062C95; DAT_08062EB4 -> 0x0806E94D; DAT_08062EB8 -> 0x080654A9.
- Thumb-bit handling and -0x10000 address-space translation are confirmed for these task pointers.
- CanTxTask creates/uses a 100 x 20-byte queue at 0x200244E0 / handle at task offset +0x0C, registered as CanMessagesToTransmit.
- CanRxTask creates/uses a 100 x 20-byte queue at 0x200244BC / handle 0x200244DC, registered as ReceivedCanMessages.
- CAN peripheral base is 0x40006800.
- FUN_08061734 directly programs CAN TX mailboxes: TSR, TIR, TDTR, TDLR, TDHR and TXRQ.
- FUN_080617DC directly reads CAN RX mailbox registers RIR/RDTR/RDLR/RDHR and builds the 20-byte RX record.
- RX producer at 0x0806F9F8 reads CAN2 via FUN_080617DC and sends the record to queue 0x200244DC.
- At least one real TX producer exists at 0x0806E59C and uses queue address 0x200244EC in the 0x0604 path.
- FUN_08011812 performs record lookup, validation and record+0x0C storage; it does not itself perform queue-send to CanMessagesToTransmit.
- FUN_0803C178 is a threshold/visibility gate using 0x10E and class-dependent thresholds; it is not evidence of dynamic CO creation.
- FUN_080480C0 is the resource/widget dispatcher used by FUN_0803E714; resource records are 16 bytes and type 1/2/3/5 dispatch to the identified helpers.
- Vtable 0x08078578 is decoded for slots +0x00,+0x04,+0x08,+0x0C,+0x10,+0x14,+0x28. Slot +0x10 is an update/tick/apply path; +0x14 is nested-object cleanup.
- IAR __iar_lz77_init3 is recovered at 0x0806E68C. Exact 108-byte runtime data at 0x20005EF0..0x20005F5B remains unresolved.

OPEN — DO NOT CLOSE WITHOUT BIN/GHIDRA EVIDENCE
- Full list of all CanMessagesToTransmit producers.
- Full parser/dispatch map of FUN_08063B80.
- ACK/SDO/protocol semantics.
- Exact 108-byte init/runtime selector region 0x20005EF0..0x20005F5B.
- Exact widget N -> TypedText 119..122 mapping.
- Exact widget N -> bitmap/callback mapping.

TRANSPORT CHAIN
CAN2 0x40006800 <-> mailbox read/write <-> 20-byte records <-> RX queue 0x200244DC / TX queue 0x200244EC <-> CanRxTask 0x0806E94C / CanTxTask 0x080654A8.

ANTI-DUPLICATION
Do not re-report already closed facts as new. Do not revive rejected hypotheses. Preserve [NEW-HARD], [CONFIRMED-REPEAT], [OPEN], [REJECTED] semantics.

IMPORTANT
The uploaded Etap 14 report is the source document for this execution. Its full text was inspected from the uploaded artifact. This manifest is the GitHub persistence marker for the turn; the next execution must continue from the OPEN list above rather than restart transport analysis.