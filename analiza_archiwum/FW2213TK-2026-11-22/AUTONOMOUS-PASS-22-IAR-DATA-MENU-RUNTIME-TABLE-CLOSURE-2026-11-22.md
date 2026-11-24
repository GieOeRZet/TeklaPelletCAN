# AUTONOMOUS PASS 22 — IAR .DATA / MENU RUNTIME TABLE CLOSURE — 2026-11-22

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Cel
Domknąć wcześniejszy OPEN dotyczący RAM 0x20005EF0..0x20005F5B oraz obu 21-bajtowych tablic MenuTree, bez zgadywania runtime bytes.

## 1. HARD — IAR LZ77 odtworzone 1:1
Źródło RAW 0x96114..0x9694D, koniec exclusive 0x9694E, 2106 B. Cel SRAM 0x20000000.
Wynik: dokładnie 0x118B3 = 71859 B, zakres 0x20000000..0x200118B2.

## 2. NEW-HARD — 0x20005EF0
00 0A 01 02 03 04 05 06 07 08 09 0B 0D 11 0F 0C 0E 12 10 13 14

## 3. NEW-HARD — 0x20005F08
00 0A 01 02 03 04 05 06 07 08 09 0B 0D 11 0F 0C 0E 12 10 13 14
Obie tablice są identyczne bajt w bajt.

## 4. NEW-HARD — obie tablice są początkowo identyczne z root-table selector
Root table RAW 0x42348 zawiera pierwszy field: 0,10,1,2,3,4,5,6,7,8,9,11,13,17,15,0,90,97,100,98,95.
Ten sam ciąg występuje w 0x20005EF0[0..20] i 0x20005F08[0..20].

### Korekta modelu
Warstwy pozostają fizycznie odrębne: root flash table, runtime class table i runtime access/update table. Jednak ich stan początkowy jest identyczny.
Zastępujemy wcześniejsze zbyt mocne zdanie 'selector != runtime class byte' precyzyjniejszym: 'selector i runtime class są odrębnymi warstwami, ale początkowo mają te same wartości'.

## 5. NEW-HARD — konfiguracja rzeczywiście steruje widocznością
Initial runtime table daje class 1..4 dla CO1..CO4, class 5 dla CWU, 6 dla solarów, 7 dla bufora, 8 dla kaskady i 9 dla dodatkowego magazynu paliwa.
RAW C064/FUN_0803C178 wiąże te klasy z parametrami konfiguracji: 1..4 -> internal 0x10E / CAN 0x2105; 5 -> 0x10F / 0x2106; 6 -> 0x110 / 0x2108; 7 -> 0x111 / 0x2107; 8 -> 0x11C; 9 -> 0x122.
To zamyka mechanizm: konfiguracja steruje eligibility/visibility konkretnych pozycji MenuTree.

## 6. Second-stage rows
Initial values: row15=0 Modulacja; row16=90 Podtrzymanie; row17=97 Praca; row18=100 Alarm; row19=98 Przepłukiwanie; row20=95 Zamarzanie.
Wartości >20 nie są bezpośrednio obsługiwane przez switch C064 0..20, więc ich dalsza nawigacja/semantyka pozostaje OPEN.

## 7. Co zostało zamknięte
- initial contents 0x20005EF0[0..20] — HARD
- initial contents 0x20005F08[0..20] — HARD
- źródło początkowych wartości — IAR LZ77 .data — HARD
- equality with root selectors — HARD
- configuration-driven visibility mechanism — HARD

## 8. OPEN
- późniejsze WRITE do obu tablic
- kiedy wartości odchodzą od initial selector values
- producer runtime access state
- dokładna semantyka rows 15..20
- exact widget/resource/callback tree po wyborze pozycji

## 9. Następny atak
P0: wszystkie RAW writes/operacje na 0x20005EF0 i 0x20005F08, szczególnie C064 i 21-iteracyjny access pass.
P1: row callback +0x26C, state-child +0x150, widget tree, visibility -> resource -> TypedText/Bitmap -> PID/CAN.