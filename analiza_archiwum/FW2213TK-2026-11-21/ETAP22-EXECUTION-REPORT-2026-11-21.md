# TEKLAPELLET-CAN — ETAP 22 — RAPORT WYKONANIA
**Data:** 2026-11-21  
**Repozytorium:** GieOeRZet/TeklaPelletCAN  
**Branch:** ccr-be8a1bcb-5t76j0  
**Firmware:** FW2213TK_kopia.bin  
**Rozmiar:** 0x1F0000 = 2,031,616 B  
**SHA-256:** 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 1. Zakres
Wykonano skrypt Etapu 22 bez zmiany zakresu zadania. Eksport został wykonany bezpośrednio z fizycznego BIN-u. Wynikowy ZIP zawiera wyłącznie trzy wymagane pliki:
- resource_table_188_clean.csv
- write_and_init_windows.txt
- can_blx_indirect_scan.txt

## 2. Wynik wykonania

### P1 — DAT_0804866C
Wyeksportowano dokładnie 188 rekordów (idx 0..187) z rekordami 16-bajtowymi, zgodnie z granicą tabeli ustaloną w Etapie 21.

Tabela TypedText została odczytana z poprawionej bazy:
0x5BE64 = 0x5BD80 + 57*4.

CSV zawiera pola:
idx, raw_off, id, f02, pl_text_fixed, f04, type, f07, f08, f0c, extra_decoded.

Dla type=3 wyciągane są ID enumów wraz z tekstami TypedText. Dla type=2 i type=5 eksportowane są surowe tablice u16.

### P2 — zapis / inicjalizacja
Wygenerowano:
write_and_init_windows.txt

Zawiera:
- szeroki skan literal-pool SRAM 0x20011300..0x20011540,
- surowe okna FUN_080373E6,
- okno silnika parametrów 0x08011100..0x08011640,
- okno callerów 0x08014400..0x080144C0,
- trzy okna inicjalizacji obszaru 0x200208EC,
- wykryte instrukcje Thumb BL wraz z adresami celów.

### P3 — BLX Rm
Wykonano pełny skan instrukcji Thumb-16 BLX Rm w zakresach:
- 0x0800D000..0x08015000
- 0x08060000..0x08070500

Wynik:
**121 trafień BLX**.

Plik:
can_blx_indirect_scan.txt

Każde trafienie zawiera adres instrukcji, rejestr Rm oraz kontekst bajtowy -16..+4.

## 3. Integralność
Firmware przeszedł oba warunki wejściowe skryptu:
- rozmiar = 0x1F0000,
- SHA-256 = 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071.

## 4. Status
[NEW-HARD] Etap 22 został wykonany zgodnie ze specyfikacją.
[CONFIRMED-REPEAT] 188 rekordów DAT_0804866C.
[CONFIRMED-REPEAT] poprawiona baza TypedText 0x5BE64 (+57 wpisów).
[NEW-HARD] 121 znalezionych instrukcji BLX Rm w dwóch zadanych zakresach.
[OPEN] Semantyka poszczególnych BLX pozostaje do analizy kontekstowej; sam fakt wystąpienia BLX nie jest dowodem na TX CAN.
[OPEN] Powiązanie bazy 0x200114C0 z konkretnym runtime object/vtable nadal wymaga dalszej analizy.

## 5. Artefakt
ETAP22_RAW_DUMP.zip został wygenerowany osobno; zawiera wyłącznie trzy pliki wynikowe wymagane przez Etap 22.

## 6. Następny krok
Priorytet dalszej analizy:
1. korelacja trafień BLX z vtable/objectami,
2. rozwiązanie ścieżki 0x200114C0 -> vptr -> slot 0,
3. dalsze szukanie brakującego UI -> CAN TX write path,
4. bez nadawania semantyki CANopen bez bezpośredniego dowodu z BIN.
