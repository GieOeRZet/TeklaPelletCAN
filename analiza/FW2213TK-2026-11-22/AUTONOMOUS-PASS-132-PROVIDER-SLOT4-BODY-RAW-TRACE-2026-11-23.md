# AUTONOMOUS PASS 132 — PROVIDER SLOT 4 BODY RAW TRACE — 2026-11-23

## Target
Provider vtable slot +0x10 -> Thumb pointer 0x080617FF -> function start 0x080617FE.

## HARD raw body
The canonical BIN shows a 38-byte routine from 0x080617FE through 0x08061823.

0x080617FE: B510
0x08061800: 4604
0x08061802: 488C
0x08061804: 6020
0x08061806: 488E
0x08061808: 6800
0x0806180A: 6801
0x0806180C: 6A49
0x0806180E: 4788
0x08061810: F104 0024
0x08061814: F000 FB30
0x08061818: F104 0010
0x0806181C: F000 FF2A
0x08061820: 4620
0x08061822: BD10

Machine-level structure:
- saves r4/lr and copies r0 into r4;
- loads literal 0x200248A4 and stores it at object offset 0;
- loads literal 0x200248A8, dereferences it twice, then calls the resulting function pointer with BLX r1;
- calls 0x08061E78 with r0 = object + 0x24;
- calls 0x08062674 with r0 = object + 0x10;
- returns the original object pointer.

Literal pool values used:
- 0x200248A4
- 0x200248A8

## XREF evidence
Raw binary scan finds exactly one 32-bit occurrence of the Thumb pointer 0x080617FF: provider vtable slot +0x10 at RAW 0x93200. There is no separate direct literal occurrence of normalized address 0x080617FE.

Called targets are independently present in function coverage:
- 0x08061E78, size 10 bytes
- 0x08062674, size 18 bytes

## Semantic boundary
The body is now closed at instruction level, but naming it state/init/persistence/destructor is not justified without surrounding object allocation/call context. The previous state/init label remains rejected as a semantic claim.

## Next
Trace 0x08061E78, 0x08062674, and RAM objects 0x200248A4/0x200248A8.