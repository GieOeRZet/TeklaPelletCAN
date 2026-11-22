# AUTONOMOUS PASS 40 — WIERSZE MENU GŁÓWNEGO ZBUDOWANE W FIRMWARE (argumenty row-buildera) — 2026-11-22

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzie: `tools/menu_rows_probe.py` (asercje). Dane: `data/menu_rows_21.csv`. Adresy: PROJECT (RUNTIME = +0x10000).

## Metoda
W emulatorze po starcie (PASS 35) wywołano **pełny konstruktor ekranu menu** PROJECT `0x0803BF7C` (RUNTIME `0x0804BF7C`; wołający konstruktor bazowy `0x08041D18` i tablicę 21×0x274 od `+0x42C`;
literał vptr `0x0808F66C` w RAW `0x3C02C`), następnie funkcję budującą wiersze `FUN_08042160` (RUNTIME `0x08052160`), przechwytując wywołania row-buildera `FUN_0804BC6C` (RUNTIME `0x0805BC6C`).
Poziom dostępu ustawiano w modelu singletonu (`FUN_080414BA() + 0x158`). Uproszczony konstruktor `0x08074508` (PASS 25) nie wystarcza: nie woła konstruktora bazowego (skok pod NULL).
Po zbudowaniu wierszy emulacja kończy się wywołaniem przez NULL (kolejne, niemodelowane obiekty) — dane wierszy są wtedy już zebrane.

## HARD — wykonanie potwierdza PASS 21/25/27
- vptr ekranu `0x0808F66C`; każdy wiersz ma vptr `0x0807C1E0` i `+0xF8 = 0x0807C540` (zgodnie z PASS 27); `+0x26C = 0`.
- **access = 0 → row-builder wywołany dla wierszy 0..14; access = 3 → dla wierszy 0..20** (15 vs 21 wywołań) — potwierdzenie wykonaniem, że wiersze 15..20 zależą od poziomu dostępu.

## HARD — argumenty row-buildera = ID bitmap (korekta PASS 39/MENUTREE)
`FUN_0804BC6C(row, A, B)` dostaje **ID bitmap**, nie ID tekstów. Pełna tabela (`data/menu_rows_21.csv`, rozmiary z `DOKUMENTACJA/bitmap_sizes.tsv`):

| wiersz | A (bitmapa) | B (bitmapa) | uwagi |
|---|---|---|---|
| 0 | 60 (34×27) | 83 (39×50) | |
| 1 | 61 (34×27) | 85 | |
| 2..5 | 62..65 | 86 (×4) | cztery wiersze z tym samym B → CO1..CO4 (rodzina instancyjna) |
| 6 | 66 | 88 | |
| 7 | 71 (367×1) | 87 | |
| 8 | 67 | 84 | |
| 9 | 70 | 82 | |
| 10 | 69 | 99 | |
| 11 | 72 | 78 | |
| 12 | 74 | 89 | |
| 13 | 77 | 159 | |
| 14 | 76 | 96 | |
| 15 | 73 (68×75) | 90 | tylko access≠0 |
| 16 | 75 | 97 | tylko access≠0 |
| 17 | 78 | 100 | tylko access≠0 |
| 18 | 79 (480×45) | 98 | tylko access≠0 |
| 19 | 80 (440×1) | 95 | tylko access≠0 |
| 20 | 81 (440×50) | 101 | tylko access≠0 |

Wcześniejszy odczyt pola „ID tekstu” z wierszy 0..14 jako nazw („Sterownik”, „Palnik”, …) był **błędnym odczytem**: te liczby to ID bitmap A. Etykiety tekstowe wierszy pochodzą z innego źródła (OPEN).

## STRONG — układ rekordów tabeli 6 B dla wierszy 15..20
Dla wierszy 0..14 builder dostaje `(A,B) = (u16@+2, u16@+4)` rekordu o stride 6 (klasa = u16@+0). Dla wierszy 15..20 dostaje `(A,B) = (u16@+4, u16@+6)`, gdzie `+6` to pierwsze pole **następnego** rekordu,
a klasa runtime = `u16@+2` (12,14,18,16,19,20 — zgodne z tablicą klas `0x20005EF0`). Wyjaśnia to wcześniejszą obserwację „klasa równa polu +2” (PASS 39). Wniosek wynika z zgodności danych (bajty tabeli ↔ argumenty ↔ tablica klas), nie z czytania pętli drugiego etapu — STRONG.
Konsekwencja: „selektory” 90, 97, 100, 98, 95 z pola +0 wierszy 16..20 nie są selektorami menu, lecz pierwszymi polami sąsiednich rekordów czytanymi jako B (bitmapy 90, 97, 100, 98, 95; ostatnie B=101 leży poza tablicą 21×6 B). Dokumenty MENUTREE traktujące je jako selektory (np. „selector 90 → Language”) są przez to NIEPEWNE.

## Wniosek dla UI
Rodzina CO1..CO4 jest zbudowana jedną ścieżką (cztery wiersze z B=86), a wiersze dla access≠0 mają osobne tło/separatory (bitmapy 79/80/81 są pasami 480×45, 440×1, 440×50). Zasoby wierszy są kompletne i znane z BIN; pozostaje powiązanie z etykietami i ekranami docelowymi.

## OPEN
1. Źródło etykiet tekstowych wierszy (TypedText) oraz ekranów docelowych (nawigacja po dotyku).
2. Dokładna pętla drugiego etapu wierszy 15..20 w `FUN_08042160` (potwierdzenie układu +2/+4/+6 z kodu).
3. Zawartość wierszy po pełnym zbudowaniu (emulacja kończy się wywołaniem przez NULL; brak obiektów z dalszych kroków).
