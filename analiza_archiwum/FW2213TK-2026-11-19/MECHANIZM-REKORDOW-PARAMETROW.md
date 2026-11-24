# FW2213TK — przełom: mechanizm indeksowania rekordów parametrów

Data: 2026-11-19

## Twardy wynik

Funkcja runtime 0x0802167A (raw 0x1167A) jest rzeczywistym wyszukiwaczem rekordów parametrów.

r1 = baza tablicy rekordów, r2 = szukany indeks.
Rekord ma rozmiar 0xB0 bajtów, a funkcja przewiduje 0x294 = 660 rekordów.

W każdym rekordzie sprawdzane są cztery pola indeksowe:
- rekord + 0x08
- rekord + 0x34
- rekord + 0x60
- rekord + 0x8C

Po znalezieniu indeksu funkcja wylicza adres:
record_base + index_position * 0x2C + 0x14

Adres ten przekazuje do funkcji 0x14728, która interpretuje wartość według typu.

## Szczegół kodu

W raw 0x1167A:
- r3 = r1 + 0x08
- odczytywane są indeksy spod r3+0x00, r3+0x2C, r3+0x58, r3+0x84
- po znalezieniu r0 jest mnożone przez 0x2C
- wynik jest dodawany do r1
- następnie dodawane jest 0x14
- adres trafia do 0x14728.

## Znaczenie dla CO1/CO2

To jest pierwszy znaleziony mechanizm, który łączy indeks parametru z konkretnym rekordem struktury i slotem danych.

Wcześniejsze 0x36FF2 było mapowaniem panelowym. 0x1167A jest znacznie bliżej właściwej warstwy danych.

## Funkcje powiązane

- 0x0802167A / raw 0x1167A — wyszukanie indeksu
- 0x080216E6 / raw 0x116E6 — analogiczna funkcja dla drugiego kierunku
- 0x0802143C / raw 0x1143C — obsługa rekordów z parametrami
- 0x08014728 / raw 0x14728 — konstrukcja/zapis wartości typowanej
- 0x08014734 / raw 0x14734 — odczyt wartości typowanej

## Korekta wcześniejszej interpretacji

0x0801825E nie powinno być traktowane jako kod parametru 0x2032. To była błędna interpretacja pola code z CSV.

Teraz mamy rzeczywisty mechanizm: 0x2167A wyszukuje indeks w rekordach o stałej strukturze.

## Czego jeszcze nie wiemy

Nie mamy jeszcze bezpośredniego dowodu, że record + 0x14 jest konkretnym adresem RAM 0x20020964.

Nie wiemy też jeszcze, czy cztery pola indeksowe odpowiadają CO1/CO2/CO3/CO4.

## Następny krok

Trzeba znaleźć bazę r1 przekazywaną do 0x1167A i odczytać rekordy dla 0x2032, 0x2033, 0x2048, 0x2049, 0x4001, 0x4002, 0x400C i 0x400D.

### Status
- [FW] rekord = 0xB0 bajtów.
- [FW] 660 możliwych rekordów.
- [FW] cztery indeksy w rekordzie, co 0x2C.
- [FW] znaleziony algorytm wyszukania indeksu.
- [FW] znaleziony adres slotu wartości po znalezieniu.
- [NIEUDOWODNIONE] dokładne znaczenie czterech slotów.
- [NIEUDOWODNIONE] RAM CO1/CO2.