# AUTONOMOUS-PASS — SIEĆ dynamiczny acceptance #1 — 2026-11-24

## Cel
Niezależne wykonanie dynamicznego testu ekranu SIEĆ na rzeczywistym firmware FW2213TK_kopia.bin, z użyciem emulatora Cortex-M/FreeRTOS + LTDC/DMA2D + I2C/FT5x06 + CAN2.

## Firmware
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
- rozmiar: 2,031,616 B

## Metoda
1. Boot rzeczywistego firmware.
2. Konfiguracja UI: PID 0x2105=4, 0x2106=1, 0x2107=1, 0x2108=1.
3. Access level = 3.
4. Wejście MENU.
5. Trzy rzeczywiste gesty swipe w celu dojścia do pozycji SIEĆ.
6. Tap pozycji SIEĆ.
7. Snapshot pustego ekranu.
8. Wstrzykiwanie ramek CAN2: heartbeat 0x700+node payload 05 oraz Identity response 0x580+node, 43 18 10 02 + u32.
9. Snapshot po zmianie + pixel diff.

## FACT-DYNAMIC — T-SIEC-56
PASS. Po wielokrotnym heartbeat 0x756 / 05 i Identity response 0x5D6 / 43 18 10 02 00 00 00 00 ekran zmienił się z pustego na:
- kolumna 1: CAN IO BIG
- kolumna 2: Node ID-86
- kolumna 3: SW v0.0
- kolumna 4: pusta w tym stanie.

To jest bezpośrednio zaobserwowany wynik firmware, nie interpretacja statyczna.
Dowód lokalny: /mnt/data/siec56/node56.png

## FACT-DYNAMIC — T-SIEC-EMPTY
PASS. Bez modułu wpisanego do tablicy dynamicznej ekran zawierał nagłówek SIEĆ i 8 pustych wierszy/slotów rozdzielonych poziomymi liniami.
Dowód lokalny: /mnt/data/siecnav/siec.png

## FACT-DYNAMIC — T-SIEC-57
OPEN / NEGATIVE IN THIS TEST. Przy samym heartbeat + Identity response dla 0x57 ekran pozostał pusty.
Dowód lokalny: /mnt/data/siec57/node57.png
Nie wolno z tego wyciągać wniosku, że firmware nigdy nie pokazuje 0x57. Test nie odtworzył jeszcze wszystkich warunków/protokołu prawdziwego CAN IO BIG.

## FACT-DYNAMIC — T-SIEC-5B
OPEN / NEGATIVE IN THIS TEST. Sam heartbeat + Identity response dla 0x5B nie spowodował wpisu.
Dowód lokalny: /mnt/data/siec5b/node5b.png
Nie zamyka to zachowania VIDE NET WIFI.

## FACT-DYNAMIC — struktura tabeli
Dla zaakceptowanego wpisu 0x56 potwierdzono rzeczywiste rozmieszczenie: nazwa modułu, tekst Node ID-<decimal>, tekst SW v<version>, a czwarta kolumna pozostaje niewypełniona dla tego wariantu.

## FACT-STATIC
- 0x56 → CAN IO BIG
- 0x57 → CAN IO BIG
- 0x5B → VIDE NET WIFI

## REJECTED
Nie używać TypedText IDs 471..474 jako semantyki kolumn SIEĆ. Dynamiczny test 0x56 potwierdził osobne źródła danych.

## OPEN
1. Dlaczego 0x57 nie pojawił się przy prostym heartbeat + 0x1018:02.
2. Jaki dokładnie warunek/protokół powoduje drugi wpis CAN IO BIG obserwowany fizycznie przez użytkownika.
3. Czwarta kolumna SIEĆ.
4. Dokładne źródło wersji SW.
5. Timeout/offline/reappearance.
6. Kolejność wielu modułów.
7. 0x5B VIDE NET WIFI i korelacja z ekranem INTERNET.
8. Wymagane identity/vendor/product values dla poszczególnych klas.

## Zmiana narzędzia
Poprawiono tools/screen_acceptance_sii.py: SIEĆ = menu row 17, INTERNET = menu row 18, INFO = menu row 12 oraz osobne tx_before i tx_after.

## Status
SIEĆ nie jest jeszcze zamknięte 100%. Ten przebieg daje pierwszy niezależny FACT-DYNAMIC dla rzeczywistego wpisu CAN IO BIG i zamyka semantykę pierwszych trzech kolumn dla tego wariantu.