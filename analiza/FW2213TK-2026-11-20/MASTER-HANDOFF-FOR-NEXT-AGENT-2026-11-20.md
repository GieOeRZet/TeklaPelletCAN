# TEKLAPELLETCAN — MASTER HANDOFF / INSTRUKCJA DLA NOWEGO AGENTA
Data: 2026-11-20
Repozytorium: GieOeRZet/TeklaPelletCAN
Firmware: FW2213TK_kopia.bin
Firmware SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

[MASTER HANDOFF content retained from previous checkpoint.]

## 26. Latest execution checkpoint — 2026-11-20 / MULTIPASS-22

The exact user-supplied Python reproduction of the IAR LZ77 loop at 0x6E68C..0x6E702 was executed against the verified firmware.

Source:
- file offset 0x96114
- script end: 0x9694E
- destination: 0x20000000

Result:
- decompressed size: 0x118B3 (71859 bytes)
- reconstructed SRAM range: 0x20000000..0x200118B3
- the exact 310-byte block 0x20011534..0x20011669 was reconstructed.

Key extracted lists:
- case 10 base (+0x90): 0x54, 0x59, 0x5A, 0x5D, 0x5C
- case 10 ext19 (+0x9C): 0x47, 0x55, 0x57, 0x89, 0x76, 0x63, 0x65, 0x77, 0x78, 0x8A, 0x69, 0x6F, 0x70, 0x73, 0x8D, 0xA5, 0xA6, 0xA7, 0x5B
- case 10 ext4 (+0x0C): 0x87, 0x79, 0x91, 0xA1

Closed branch:
- 0x47 = case 10 (Palnik), access gate +0x158 != 0, first item of the 19-element list at 0x200115D0.
- 0x48 = case 0 (Kocioł), access gate +0x158 != 0, first item of the 10-element list at 0x200115B0.
- The hypothesis that 0x48 belongs to the five case-10 base IDs is REJECTED.

The complete raw 310-byte block is stored in:
analiza/FW2213TK-2026-11-20/MULTIPASS-22-IAR-LZ77-DATA-CLOSURE-AND-480C0-2026-11-20.md

### FUN_080480C0 follow-up

Raw Thumb disassembly 0x480C0..0x48422 was executed.

Hard raw observations:
- incoming parameter-list pointer is stored through object+0x84EC/+0x84F0;
- list count is held at object+0x3B8;
- entries are loaded as signed halfwords;
- each list value is scanned against a 0xBC-entry table;
- each table record is 0x10 bytes wide;
- comparisons use record halfwords at +0x00, +0x10, +0x20, +0x30 relative to the table record base;
- exact 0xBC match wraps to index 0;
- selected record fields +0x02/+0x04/+0x06/+0x07/+0x08/+0x0C are consumed;
- +0x06 dispatches cases 1, 2, 3 and 5;
- case 1 calls 0x4E598 and stores a pointer at object+0x270;
- cases 2 and 5 call 0x4E740;
- case 3 calls 0x4E75A;
- repeated 0x338-byte child objects are built at object+0x42C.

No direct literal comparison with 0x47 or 0x48 was observed in this raw function window. Therefore the requested dynamic-filter question for 0x48 remains OPEN until downstream helpers/table semantics are traced.

Next execution target:
1. 0x4E4F8
2. 0x4E598
3. 0x4E740
4. 0x4E75A
5. the table around the ADR-derived address used by 0x480C0
6. identify whether row visibility/filtering can suppress 0x48 after FUN_0803E714 populates presenter+0x20.

Full report:
analiza/FW2213TK-2026-11-20/MULTIPASS-22-IAR-LZ77-DATA-CLOSURE-AND-480C0-2026-11-20.md

Workflow rule remains:
- external deep-analysis agent performs semantic analysis;
- this assistant executes requested BIN/Git extraction and verification;
- raw requested material is returned as one copyable block when asked;
- do not replace the external agent's semantic analysis unless explicitly instructed to consolidate/analyze independently.
