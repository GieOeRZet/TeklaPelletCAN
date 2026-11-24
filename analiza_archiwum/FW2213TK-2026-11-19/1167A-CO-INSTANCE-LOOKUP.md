Analiza FW2213TK — dynamiczne wyliczanie indeksu instancji przed 0x1167A

NOWY TWARDY DOWÓD

W kodzie raw 0x370C0 firmware nie wyszukuje bezpośrednio stałego indeksu bazowego. Dla wpisu tabeli bierze bazowy indeks z pola +0x02, pobiera bajt instancji/modułu z globalnego obiektu wskazywanego przez literal raw 0x3754C (0x200248D4), dodaje ten bajt i odejmuje 1. Wynik trafia do r2 funkcji 0x1167A.

Raw 0x370E8..0x37100:
ldrh r0,[r7,#2]
ldrb r1,[r6,#1]
adds r0,r0,r1
subs r2,r0,#1
uxth r2,r2
r1 = 0x200248D4
BL 0x1167A

Czyli dla bazy 0x2032 i instancji 2 lookup dostaje dokładnie 0x2033. Analogicznie 0x2048 -> 0x2049, 0x2064 -> 0x2065, 0x4001 -> 0x4002.

TO WYJAŚNIA wcześniejszy brak literalnych 0x2033/0x2049/0x2065 w rejestracji: indeks instancji jest tworzony dynamicznie podczas lookup.

MECHANIZM

Etap A — rejestracja: 0x1143C tworzy rekord 0x2C i zapisuje +0x08=index, +0x0C=r2/source, +0x10=typ oraz +0x14/+0x1C/+0x24 wartości/obiekty.

Etap B — wybór instancji: 0x370C0 wykonuje base_index + instance - 1, a następnie 0x1167A szuka tego indeksu w rekordach oddalonych o 0x2C.

DLA CO2

Dla rodziny 0x2032..0x2035 sposób wywołania CO2 jest już twardo potwierdzony:
0x2032 + 2 - 1 = 0x2033.

To samo:
0x2048 + 2 - 1 = 0x2049
0x2064 + 2 - 1 = 0x2065
0x4001 + 2 - 1 = 0x4002

Nadal otwarte jest tylko to, skąd w tablicy rekordów pojawiają się rekordy 0x2033/0x2034/0x2035. Nie należy już szukać wyłącznie literalnych rejestracji tych indeksów. Trzeba znaleźć mechanizm klonowania/uzupełniania rekordów albo budowy tablicy instancji.

STATUS
[FW] 0x370C0 dynamicznie tworzy indeks instancji.
[FW] 0x1167A wybiera rekord po tym indeksie.
[FW] cztery rekordy są oddalone o 0x2C.
[FW] CO2 dla bazy 0x2032 daje 0x2033.
[NIEUDOWODNIONE] sposób utworzenia rekordów 2–4.
[NIEUDOWODNIONE] RAM CO2.
