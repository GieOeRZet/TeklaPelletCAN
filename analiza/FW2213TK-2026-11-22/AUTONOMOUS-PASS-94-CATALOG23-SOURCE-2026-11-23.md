# PASS 94 — Katalog 23 wartości: źródło tablicy

## Wynik
**FACT/STRONG:** wskaźnikowa tablica katalogu 23 elementów zaczyna się pod `0x20008C50` i zawiera 23 u32 pointery do rekordów `0x20008AE0..0x20008C40`, ze stałym krokiem `0x10`. Wartość katalogowa jest pobierana z `[pointer+0x08]`.

Kolejność wartości:
`10, 18, 120, 180, 230, 12, 15, 25, 35, 50, 75, 2000, 2500, 3000, 16, 30, 150, 220, 300, 500, 1550, 1220, 1300`.

Rekord #23 to `0x20008C40`, a jego wartość `[0x20008C48] = 1300`. Wcześniejsze założenie o `0x20008EFC` jako rekordzie #23 jest REJECTED.

## Znaczenie
Tablica jest katalogiem wartości Parameters set Number używanym przez `FUN_080144B4/FUN_080144E4`. `0x20008EFC` jest innym obiektem/rekordem.

## Dowód
Zrzut RAM/emulatora przekazany przez Claude 2026-11-23 wskazuje dokładnie 23 rekordy od `0x20008AE0`, krok `0x10`, oraz wartości `[+8]`. Wynik zapisano w `cg_catalog23.csv`.
