# FW2213TK — przełom w mechanizmie rekordów, 2026-11-19

## Najważniejsze nowe ustalenie

Wcześniejsze założenie, że każdy rekord parametru powstaje wyłącznie w jednej statycznej tablicy, jest zbyt wąskie.

Funkcja 0x1167A jest wywoływana z czterech miejsc:
- raw 0x0D72C
- raw 0x10138
- raw 0x370FE
- raw 0x37138

Dwa pierwsze używają baz tablic pobieranych z obiektów, a nie stałego 0x20008D84.

Szczególnie ważny jest raw 0x10138:
- r1 = [r4 + 0x04]
- r2 = r5
- BL 0x1167A

Czyli lookup może działać na tablicy rekordów należącej do konkretnego obiektu, a nie tylko na głównej tabeli.

## Co potwierdza 0x11812

0x11812 nie tworzy nowych rekordów. Szuka istniejącego rekordu po indeksie i zapisuje wartość do źródła wskazanego przez record+0x0C.

Dla typu źródła:
- typ 1 -> zapis 8-bit
- typ 2 -> zapis 16-bit
- typ 3/4 -> zapis 16-bit
- typ 5 -> zapis 32-bit.

To jest bezpośredni dowód, że record+0x0C jest wskaźnikiem na właściwą zmienną RAM / storage parametru.

## Nowy trop

Konstruktor obiektu modułu raw 0x37CA4 ustawia:
- module+0x108 jako strukturę pomocniczą,
- module+0x128 = {1,0,0},
- module+0x158 = 0,
- przekazuje dwa argumenty do obiektu pomocniczego przy +0x108.

Następnie 0x39394 inicjalizuje strukturę pomocniczą: pointer/vtable, zeruje +4 i kopiuje 8 bajtów z globalnej struktury do +8.

## Wniosek

Statyczna rejestracja 0x1143C nie klonuje rekordu 0x2032 na 0x2033..0x2035.
Trzeba znaleźć obiektową tablicę używaną przez wywołanie 0x1167A z raw 0x10138 albo 0x0D72C. To jest obecnie najlepszy punkt do złapania realnego record+0x0C dla instancji CO2.

## Status dowodu

[FW] Pewne:
- 0x2033 jest wynikiem 0x2032 + instance - 1.
- record+0x0C jest storage pointerem używanym przez zapis parametru.
- istnieją obiektowe tablice rekordów używane przez 0x1167A.

[NIEUSTALONE]:
- dokładny adres RAM CO2 dla 0x2033.
- czy storage CO2 znajduje się bezpośrednio w obiekcie modułu, czy w obiekcie powiązanym.