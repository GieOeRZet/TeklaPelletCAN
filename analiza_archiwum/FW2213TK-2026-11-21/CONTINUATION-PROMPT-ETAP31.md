# TEKLAPELLET-CAN — START NOW / ETAP 31

Pracujesz nad repozytorium GieOeRZet/TeklaPelletCAN, branch ccr-be8a1bcb-5t76j0.

Najpierw przeczytaj:
analiza_archiwum/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-30-ESP32C6.md

Nie zaczynaj reverse engineeringu od zera i nie powtarzaj Etapów 1–30 bez konkretnej potrzeby.

Firmware:
FW2213TK_kopia.bin
size 0x1F0000
SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Zasady:
- rozdzielaj [NEW-HARD], [CONFIRMED-REPEAT], [NEW-STRONG], [OPEN], [REJECTED];
- nie zamykaj [OPEN] bez bezpośredniego dowodu z BIN;
- nie zakładaj CANopen/SDO bez dowodu;
- nie traktuj każdego BLX jako CAN TX;
- korzystaj z istniejących RAW dumpów;
- wyniki każdego większego etapu dokumentuj w analiza_archiwum/.

PIERWSZY CEL:
Rozwiąż dokładnie łańcuch:

0x200114C0
→ [obj+0]
→ vptr
→ vtable slot 0
→ konkretny BLX target
→ TX adapter
→ CanMessagesToTransmit
→ CanTxTask
→ FUN_08061734
→ CAN2

Punkt startowy:
0x080100BE..0x080100C6:
add r1,sp,#8
ldr r0,[r4]
ldr r2,[r0]
ldr r2,[r2]
blx r2

Kolejne cele:
1. rozwiązać runtime initialization [0x200114C0+0],
2. znaleźć rzeczywisty vptr,
3. znaleźć slot 0,
4. znaleźć jego konkretny target,
5. prześledzić target aż do TX queue/CAN2,
6. dopiero potem przejść do pozostałych 11 rodzin RX i pełnej tabeli CAN.

Nie uznawaj głównej architektury TX za zamkniętą przed rozwiązaniem tego łańcucha.
