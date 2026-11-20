# MULTIPASS-22 — IAR LZ77 DATA CLOSURE + FUN_080480C0 FOLLOW-UP
Data: 2026-11-20
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 1. IAR LZ77 execution result

Executed the exact user-supplied Python 1:1 reproduction of the loop at 0x6E68C..0x6E702 against /mnt/data/FW2213TK_kopia.bin.

Source:
- file offset 0x96114
- script end expression: 0x96114 + (0x1074 >> 1) = 0x9694E
- destination base: 0x20000000

Result:
- decompressed size: 0x118B3 (71859 bytes)
- reconstructed SRAM range: 0x20000000 .. 0x200118B3
- target 310-byte block 0x20011534..0x20011669 is inside the reconstructed data.

Exact reconstructed 310-byte block:

20011534: 25 01 08 00 02 00 49 01 26 01 00 00 87 00 79 00
20011544: 91 00 A1 00 06 01 07 01 08 01 09 01 5E 01 60 01
20011554: 63 01 64 01 03 01 04 01 05 01 00 00 61 01 65 01
20011564: 5F 01 00 00 90 00 6A 01 14 01 12 01 13 01 0E 01
20011574: 0D 01 0F 01 10 01 11 01 15 01 16 01 48 01 1A 01
20011584: 1B 01 12 00 1C 01 1D 01 22 01 1F 01 33 01 00 00
20011594: 58 01 4D 01 4E 01 4F 01 50 01 51 01 52 01 53 01
200115A4: 54 01 00 00 0F 00 14 00 15 00 00 00 48 00 11 00
200115B4: 16 00 18 01 19 01 26 00 28 00 4B 01 2E 00 2F 00
200115C4: 54 00 59 00 5A 00 5D 00 5C 00 00 00 47 00 55 00
200115D4: 57 00 89 00 76 00 63 00 65 00 77 00 78 00 8A 00
200115E4: 69 00 6F 00 70 00 73 00 8D 00 A5 00 A6 00 A7 00
200115F4: 5B 00 00 00 A9 00 AA 00 BE 00 B1 00 AF 00 BC 00
20011604: B4 00 B5 00 B6 00 B7 00 D3 00 D4 00 AD 00 AE 00
20011614: B0 00 B3 00 B2 00 B8 00 BA 00 B9 00 BB 00 BD 00
20011624: CC 00 00 00 D9 00 DA 00 DD 00 DE 00 E3 00 E7 00
20011634: E5 00 E6 00 DF 00 E0 00 E2 00 E1 00 F3 00 F4 00
20011644: F6 00 F7 00 9C 00 9D 00 FC 00 00 00 9A 01 9B 01
20011654: 9C 01 9D 01 9E 01 9F 01 A0 01 A1 01 A2 01 A3 01
20011664: A5 01 A6 01 A7 01

## 2. Extracted class-10 values from the exact block

class 10 base at +0x90:
0x54, 0x59, 0x5A, 0x5D, 0x5C

class 10 ext19 at +0x9C:
0x47, 0x55, 0x57, 0x89, 0x76, 0x63, 0x65, 0x77, 0x78, 0x8A, 0x69, 0x6F, 0x70, 0x73, 0x8D, 0xA5, 0xA6, 0xA7, 0x5B

class 10 ext4 at +0x0C:
0x87, 0x79, 0x91, 0xA1

## 3. Closed branch record

Based on the reconstructed RAM block and previously established FUN_0803E714 list layout, the current branch closure recorded here is:

- 0x47: case 10 (Palnik), access gate +0x158 != 0, first entry of the 19-element list at 0x200115D0 (+0x9C).
- 0x48: case 0 (Kocioł), access gate +0x158 != 0, first entry of the 10-element list at 0x200115B0 (+0x7C).
- The earlier hypothesis that 0x48 belongs to the five base IDs of case 10 is rejected.

The complete list map is retained in the master handoff and prior FUN_0803E714 reports.

## 4. FUN_080480C0 execution follow-up

Executed raw Thumb disassembly:
llvm-objdump -D --triple=thumbv7m --start-address=0x480c0 --stop-address=0x48422

Observed raw facts relevant to the requested follow-up:
- function range: 0x480C0..0x48422
- stores the incoming list pointer at object+0x84F0 (via object+0x84EC, then +4)
- iterates a count held at object+0x3B8
- each list entry is loaded as signed halfword from the stored list
- scans a table pointed to by ADR-derived data around 0x48668, comparing each list value against table halfwords at offsets 0x00, 0x10, 0x20, 0x30
- the scan has a 0xBC-entry bound and wraps an exact 0xBC match to index 0
- selected record fields at offsets +0x02, +0x04, +0x06, +0x07, +0x08, +0x0C are consumed
- selected record +0x06 dispatches cases 1,2,3,5
- case 1 calls 0x4E598 and stores object-relative function/resource pointer at +0x270
- cases 2 and 5 call 0x4E740
- case 3 calls 0x4E75A
- the function builds repeated 0x338-byte objects at object+0x42C
- no direct comparison against literal 0x47 or 0x48 was observed in this raw function window
- this pass therefore does NOT close or reject the possibility of a downstream dynamic filter for 0x48.

Full raw disassembly used for this report was obtained directly from the firmware ELF wrapper and is preserved in the analysis session.

## 5. Status

HARD:
- exact IAR decompression result and 310-byte reconstruction
- exact locations of 0x47 and 0x48 in the reconstructed lists, as above

OPEN:
- whether FUN_080480C0 or its downstream helpers dynamically suppress a row after the parameter list has been built
- exact semantic mapping of the table consumed by FUN_080480C0
- whether any equipment/module gate specifically removes 0x48 after list construction

Next execution target:
- continue from FUN_080480C0 into 0x4E4F8 / 0x4E598 / 0x4E740 / 0x4E75A and the table around the ADR-derived address, looking specifically for row creation/visibility behavior and any 0x48-specific condition.
