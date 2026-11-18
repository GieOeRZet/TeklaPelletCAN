# FW2213TK — dalsze rozdzielenie mapowania panelowego od RAM

Data: 2026-11-19

## Ważna korekta interpretacji funkcji 0x08046FF2

Po prześledzeniu wywołań raw 0x36FF2 / runtime 0x08046FF2 wiadomo już, że jej wynik jest używany przez warstwę obiektów panelu.

Schemat w dużym fragmencie firmware:
1. obiekt nadrzędny ma wskaźnik pod +0x08,
2. ten wskaźnik trafia do 0x36FF2 jako r0,
3. indeks parametru trafia jako r1,
4. 0x36FF2 zwraca numer/slot,
5. wynik jest przekazywany dalej do obiektu pod +0x0C.

Przykładowe indeksy używane w tym mechanizmie: 0x68, 0x39, 0xAC, 0x10E, 0xD7, 0xDC, 0x10F, 0x147, 0x14C, 0x111, 0x121, 0x133, 0x134, 0x14A, 0x149, 0x148, 0x137, 0x136.

To pokazuje, że 0x36FF2 jest przede wszystkim funkcją indeks parametru -> panelowy slot/ID dla konkretnego kontekstu, a nie bezpośrednim getterem RAM.

## Co nadal jest twarde

W 0x36FF2:
- odczyt context + 0x12C jest rzeczywisty,
- tabela specjalna ma 49 wpisów,
- wynik dla wpisu to slot + context[0x12C] - 1,
- druga tabela ma 420 wpisów.

Nie wolno jeszcze utożsamiać panel slot z adresem RAM.

## Nowy kierunek

Próba znalezienia bezpośrednich literałów adresów RAM 0x200209xx nie znalazła tych pełnych adresów jako stałych w BIN.

To oznacza, że dalsze szukanie musi iść przez wskaźnik/bazę struktury, a nie przez wyszukiwanie pełnych adresów RAM.

## Status dowodów

- [FW] 0x36FF2 = mapowanie indeksu parametru na slot/ID zależny od kontekstu.
- [FW] +0x12C wpływa na wynik mapowania.
- [FW] wynik 0x36FF2 jest używany dalej przez obiekty panelowe.
- [FW] pełnych adresów 0x200209xx nie znaleziono jako literalnych stałych.
- [NIEUDOWODNIONE] 0x36FF2 mapuje bezpośrednio do RAM.
- [NIEUDOWODNIONE] stały stride RAM CO1/CO2.

Następny cel: znaleźć bazę struktury danych parametrów oraz funkcję odczytu/zapisu, która dostaje indeks/deskryptor i dereferencjuje wskaźnik danych.