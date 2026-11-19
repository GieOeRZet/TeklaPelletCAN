# FW2213TK — kluczowa korekta: record+0x0C wskazuje deskryptor wartości, 2026-11-19

## Przełom

Analiza 0x14700–0x14728 oraz 0x11812 pokazuje, że `record+0x0C` nie jest bezpośrednio zmienną wartości.

Deskryptor ma co najmniej 5 bajtów:
- +0x00 = aktualna wartość / storage (1, 2 albo 4 bajty zależnie od typu),
- +0x04 = typ danych.

Funkcje pomocnicze:
- 0x14700: zapis 32-bit + typ 5,
- 0x14708: zapis 16-bit + typ 2,
- 0x14710: zapis 8-bit + typ 1,
- 0x14718: zapis 16-bit + typ 4,
- 0x14720: zapis 32-bit + typ 3,
- 0x14728: kopiuje 5-bajtowy deskryptor.

0x11812 po znalezieniu rekordu robi:
`r7 = record + 0x0C` -> odczyt typu z `[r7+4]` -> odczyt/zapis wartości przez `[r7]`.

## Konsekwencja dla CO1

Dla CO1 rejestracja:
- 0x2032 -> r2 = 0x20020964
- 0x2048 -> r2 = 0x20020966
- 0x2064 -> r2 = 0x2002096E

oznacza więc, że te adresy są adresami deskryptorów parametrów, a niekoniecznie finalnym adresem fizycznej zmiennej wartości.

To wyjaśnia, dlaczego wcześniejsze traktowanie pola CSV `RAM` jako bezpośredniego storage było zbyt mocne.

## Co to zmienia dla CO2

Poszukiwany adres CO2 nie musi być `CO1_RAM + stride`.
Musimy znaleźć deskryptor przypisany rekordowi `0x2033` i dopiero jego `[+0]` daje właściwe storage wartości.

Jednocześnie nadal obowiązuje twardy dowód:
`0x2033 = 0x2032 + instance - 1`.

## Bardzo ważny model danych

`CAN index -> record (0x2C) -> descriptor (+0x0C) -> value/type`.

To jest obecnie najdokładniejszy model mechanizmu parametrów wynikający bezpośrednio z firmware.