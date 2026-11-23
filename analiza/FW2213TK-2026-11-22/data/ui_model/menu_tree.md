# Drzewo menu (szkielet, PASS 65)

Legenda dowodow: MEASURED / STRONG / DOC / OPEN. Pelne dane: `menu_tree.json`.

## HOME
- HOME -> MENU (kafel MENU), kafle: Paliwo, plomien, Ogrzewanie 1/2, Woda, zasilanie, AUTO, zegar (DOC; wiazania OPEN)

## MENU (21 wierszy)

| # | wiersz | cel | klasa runtime | poziom min | warunek konfiguracji | dowod |
|---|---|---|---|---|---|---|
| 0 | Kociol | KOCIOL | 0 | 0 | - | STRONG |
| 1 | Palnik | PALNIK | 10 | 0 | - | STRONG |
| 2 | Ogrzewanie 1 | OGRZEWANIE | 1 | 0 | 0x2105 >= 1 | STRONG |
| 3 | Ogrzewanie 2 | OGRZEWANIE | 2 | 0 | 0x2105 >= 2 | STRONG |
| 4 | Ogrzewanie 3 | OGRZEWANIE | 3 | 0 | 0x2105 >= 3 | STRONG |
| 5 | Ogrzewanie 4 | OGRZEWANIE | 4 | 0 | 0x2105 >= 4 | STRONG |
| 6 | Ciepla woda | CWU | 5 | 0 | 0x2106 != 0 | STRONG |
| 7 | Solary | SOLARY | 6 | 0 | 0x2108 != 0 | STRONG |
| 8 | Bufor | BUFOR | 7 | 0 | 0x2107 != 0 | STRONG |
| 9 | Kaskada | KASKADA | 8 | 0 | 0x350C != 0 | STRONG |
| 10 | Dodatkowy magazyn paliwa | MAGAZYN | 9 | 0 | 0x3525 != 0 | STRONG |
| 11 | Historia alarmow | ALARMY | 11 | 0 | - | STRONG |
| 12 | Informacje o programie | INFO | 13 | 0 | - | STRONG |
| 13 | Konfiguracja | KONFIGURACJA | 17 | 0 | - | STRONG |
| 14 | Poziom menu (PIN) | DLG_PIN | 15 | 0 | - | STRONG |
| 15 | Jezyk (Language) | (kontrolka w wierszu) | 12 | 1 | - | STRONG |
| 16 | Alarm dzwiekowy (przelacznik) | (kontrolka w wierszu) | 14 | 1 | - | STRONG |
| 17 | Test wyjsc | TEST_WYJSC | 18 | 1 | - | STRONG |
| 18 | Statystyki | STATYSTYKI | 16 | 1 | - | STRONG |
| 19 | Siec | SIEC | 19 | 1 | - | STRONG |
| 20 | Internet | INTERNET | 20 | 1 | - | STRONG |

## Krawedzie zmierzone (poziom 0)

| z | dotyk | cel | opis |
|---|---|---|---|
| KOCIOL | [65, 22] | MENU | przycisk powrotu < (naglowek, widget 130x45) |
| KOCIOL | [479, 25] | HOME | ikona domu (prawy gorny rog) |
| KOCIOL | [91, 20] | MENU | napis < MENU (naglowek) |
| KOCIOL | [414, 130] | PROGRAM | pasek programu (PROGRAM) |
| KOCIOL | [359, 249] | LISTA | kafel zebatki (NASTAWY) |
| LISTA | [65, 22] | ORIGIN | przycisk powrotu < (naglowek, widget 130x45) |
| LISTA | [479, 25] | HOME | ikona domu (prawy gorny rog) |
| LISTA | [41, 26] | ORIGIN | dotyk widgetu (niezidentyfikowany) |
| LISTA | [91, 20] | ORIGIN | napis < MENU (naglowek) |
| LISTA | [26, 43] | ORIGIN | dotyk widgetu (niezidentyfikowany) |
| LISTA | [77, 43] | ORIGIN | dotyk widgetu (niezidentyfikowany) |
| LISTA | [128, 43] | ORIGIN | dotyk widgetu (niezidentyfikowany) |
| PALNIK | [65, 22] | MENU | przycisk powrotu < (naglowek, widget 130x45) |
| PALNIK | [479, 25] | HOME | ikona domu (prawy gorny rog) |
| PALNIK | [91, 20] | MENU | napis < MENU (naglowek) |
| PALNIK | [359, 249] | LISTA | kafel zebatki (NASTAWY) |
| OGRZEWANIE | [65, 22] | MENU | przycisk powrotu < (naglowek, widget 130x45) |
| OGRZEWANIE | [479, 25] | HOME | ikona domu (prawy gorny rog) |
| OGRZEWANIE | [91, 20] | MENU | napis < MENU (naglowek) |
| OGRZEWANIE | [414, 130] | PROGRAM | pasek programu (PROGRAM) |
| OGRZEWANIE | [359, 249] | LISTA | kafel zebatki (NASTAWY) |
| HOME | None | MENU | kafel MENU (34,235) |

## Listy NASTAWY: liczba pozycji wg poziomu 0/1/2/3

- klasa 0x00: {'0': 3, '1': 13, '2': 13, '3': 13}
- klasa 0x01: {'0': 12, '1': 23, '2': 23, '3': 23}
- klasa 0x02: {'0': 12, '1': 23, '2': 23, '3': 23}
- klasa 0x03: {'0': 12, '1': 23, '2': 23, '3': 23}
- klasa 0x04: {'0': 12, '1': 23, '2': 23, '3': 23}
- klasa 0x05: {'0': 8, '1': 12, '2': 12, '3': 12}
- klasa 0x06: {'0': 3, '1': 7, '2': 7, '3': 7}
- klasa 0x07: {'0': 2, '1': 7, '2': 7, '3': 7}
- klasa 0x08: {'0': 9, '1': 9, '2': 9, '3': 9}
- klasa 0x09: {'0': 4, '1': 7, '2': 7, '3': 7}
- klasa 0x0A: {'0': 5, '1': 24, '2': 28, '3': 28}
- klasa 0x10: {'0': 5, '1': 24, '2': 26, '3': 26}
- klasa 0x11: {'0': 13, '1': 13, '2': 13, '3': 13}

## OPEN

- HOME: wiazania widgetow, okna (Paliwo, zasilanie, AUTO) - vtable/widgety nie zmierzone
- PROGRAM: widgety i wiazania (harmonogram 7 dni x 24 h)
- Kaskada, Dodatkowy magazyn paliwa: odslonic konfiguracja 0x350C/0x3525, zmierzyc
- Warunki wierszy menu wg konfiguracji (0x2105..0x2108, 0x350C, 0x3525): zmierzyc przegladem wartosci
- Poziomy 1 i 3: inwentarz widgetow (mamy L0 i L2); poziom 3 = tylko CPU% w naglowku + 6 wrapperow
- Graf akcji: tylko 6 z 24 wezlow L0 (232 stukniecia); brak pozostalych klas i klas poza menu
- Dialogi: vtable, widgety, wiazania, ramki TX (PIN, Paliwo, czas, edycja, zasilanie, AUTO, potwierdzenia, bledy)
- Wiersze 15/16 (Jezyk, Alarm dzwiekowy): kontrolki wbudowane w wiersz (nie ekran)
- Alarmy: warunki per alarm, prezentacja, ACK
- Wykresy/Statystyki: widoki i dane
