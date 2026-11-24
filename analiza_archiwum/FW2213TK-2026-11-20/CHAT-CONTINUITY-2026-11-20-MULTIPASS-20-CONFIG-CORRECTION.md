# CHAT CONTINUITY — 2026-11-20 — MULTIPASS 20 CONFIG/ACCESS CORRECTION

## Co wykonano w tym przebiegu

Wykonano wielotorowy cross-check konfiguracji firmware:
- internal index -> CAN,
- 0x2105..0x2108,
- FUN_0803C178,
- 21-slot menu construction,
- access levels 0..3,
- 6154,
- CO1..CO4,
- oficjalna dokumentacja Estyma/Tekla,
- stale-hypothesis audit.

## Najważniejsza korekta

Aktualny mapping:

- 0x10D -> 0x3505 = Outside temperature sensor configuration
- 0x10E -> 0x2105 = Heating configuration
- 0x10F -> 0x2106 = Hot water configuration
- 0x110 -> 0x2108 = Solar configuration
- 0x111 -> 0x2107 = Buffer configuration

Starsze batch notes z 2026-11-19 zawierające 0x10E -> 0x3505 / 0x10F -> 0x2105 są historyczne i superseded.

## Nowe zamknięcie 2105

FUN_0803C178:

- selector 1 -> 0x2105, threshold >=1 -> CO1
- selector 2 -> 0x2105, threshold >=2 -> CO2
- selector 3 -> 0x2105, threshold >=3 -> CO3
- selector 4 -> 0x2105, threshold >=4 -> CO4

To jest bezpośredni firmware-level capability/visibility fan-out.

Nie wolno jednak pisać jeszcze:
0x2105 -> C064 -> +0x12C.

To nadal OPEN.

## 21-slot menu

Tabela @ 0x42348 ma 21 rekordów.
- records 0..14: pierwszy etap,
- records 15..20: drugi etap, tylko gdy access != 0,
- potem 21-slot capability/update passes,
- row stride = 0x274.

## Access

- 0 -> level 0
- 900 -> level 1
- 999 -> level 2
- 6154 -> level 3

6154 nie tworzy samych sześciu second-stage rows; one wymagają access != 0.
6154 ma osobne >=3 gates, które dodają + control do 17 UI paths.

## Dokumentacja producenta

Instrukcja Estyma/Tekla potwierdza:
- „Ilość obwodów grzewczych” określa liczbę obwodów CO,
- IgneoTouch obsługuje do 4 obwodów CO,
- profile i hardware/module type są osobnymi osiami konfiguracji.

## Aktualny model

hardware/module discovery
 -> profile/variant
 -> functional configuration
 -> capability resolver
 -> access resolver
 -> 21 row slots
 -> screen dispatcher
 -> class/type + instance
 -> instance-aware parameter engine
 -> record/CAN/storage
 -> widget/touch/write

## Najbliższe ataki

1. param_2 -> C064 -> class 1..4
2. exact selector 1..4 -> click/navigation -> CO screen factory
3. CO screen -> +0x12B/+0x12C
4. 0x10D / 0x3505 full consumer graph
5. 17 x 6154 numeric-editor bindings
6. trailing selectors 90/97/100/98/95/0 consumer mapping
7. 370A dopiero po ustabilizowaniu configuration spine

Pełny raport:
`analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-20-DEEP-CONFIG-ACCESS-SOURCE-OF-TRUTH-2026-11-20.md`

Branch: ccr-be8a1bcb-5t76j0
