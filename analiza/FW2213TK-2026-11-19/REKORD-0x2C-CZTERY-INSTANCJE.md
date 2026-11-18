# FW2213TK — korekta: rekord ma 0x2C, a 0x1167A wybiera jedną z 4 kolejnych instancji

Data: 2026-11-19

## Najważniejsze

Dokładny disassembly 0x1143C i 0x1167A pozwolił poprawić wcześniejszy opis.

**0x1143C** jest funkcją rejestrującą pojedynczy rekord parametru. Pojedynczy rekord ma **0x2C bajtów**.

Układ istotnych pól pojedynczego rekordu:
- +0x08: uint16 indeks parametru
- +0x0C: wskaźnik przekazany w r2 — to jest osobny wskaźnik danych/źródła wartości
- +0x10: typ/klasyfikacja rekordu
- +0x14: wartość/obiekt używany jako wynik dla pierwszej pozycji
- +0x1C: analogiczny slot
- +0x24: analogiczny slot
- +0x28/+0x2A: pozostałe pola rekordu zależne od typu

## 0x1167A

Funkcja dostaje:
- r0 = bufor wyjściowy
- r1 = baza tablicy rekordów
- r2 = szukany indeks.

Przeszukuje cztery indeksy w każdym rekordzie/ciągu:
- rekord +0x08
- rekord +0x34
- rekord +0x60
- rekord +0x8C

Te adresy są dokładnie oddalone o 0x2C, więc oznaczają cztery kolejne rekordy.

Po znalezieniu pozycji n = 0..3:
`adres = baza + n*0x2C + 0x14`

Następnie adres jest przekazywany do 0x14728.

## Bardzo ważna konsekwencja dla CO1/CO2

Jeżeli parametry `0x2032..0x2035` są zarejestrowane jako rodzina czterech rekordów, mechanizm nie liczy RAM CO2 jako `RAM_CO1 + arbitralny stride`.

Zamiast tego każdy indeks ma własny rekord, a rekord ma własny wskaźnik danych pod +0x0C.

To jest znacznie mocniejszy model:

`CAN index -> rekord 0x2C -> wskaźnik danych +0x0C`

oraz osobno:
`CAN index -> slot wartości +0x14 -> 0x14728/0x14734`

## Twardy dowód z 0x1143C

Po znalezieniu wolnego rekordu funkcja:
- zapisuje indeks do `record+0x08`,
- zapisuje r2 do `record+0x0C`,
- zapisuje typ/parametry rekordu,
- zapisuje dane/wartości do `record+0x14`, `+0x1C`, `+0x24`.

To bezpośrednio pokazuje, że r2 jest częścią rekordu i jest przekazywane przez rejestrację.

## Baza tabeli

W wywołaniu z raw 0x370FE funkcja 0x1167A dostaje bazę **0x200248D4**. Jest to RAM-owa tablica rekordów, a nie tabela Flash.

To ważne: zawartość tej tablicy jest budowana podczas pracy firmware.

## Co jeszcze trzeba znaleźć

Teraz trzeba znaleźć moment, w którym do 0x1143C rejestrowane są konkretne indeksy CO oraz wartość r2 dla nich.

Interesujące rodziny:
- 0x2032..0x2035
- 0x2048..0x204B
- 0x2064..0x2067
- 0x4001..0x4004
- 0x400C..0x400F

Jeżeli r2 dla tych rekordów okaże się wskaźnikiem do bloku `0x200209xx`, otrzymamy bezpośredni CAN index -> RAM.

## Status

- [FW] pojedynczy rekord rejestracji = 0x2C bajtów.
- [FW] +0x08 = indeks.
- [FW] +0x0C = wskaźnik przekazany przez r2.
- [FW] 0x1167A wybiera jedną z czterech kolejnych instancji co 0x2C.
- [FW] baza 0x200248D4 jest rzeczywistą RAM-ową tablicą używaną przez jedno z wywołań 0x1167A.
- [NIEUDOWODNIONE] że cztery kolejne rekordy zawsze oznaczają CO1..CO4.
- [NIEUDOWODNIONE] że r2 dla CO1/CO2 wskazuje bezpośrednio na 0x200209xx.
- [NIEUDOWODNIONE] dokładny RAM CO2.