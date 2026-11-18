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

## Nowy twardy dowód: rejestracja CO1 i źródło RAM

W funkcji rejestrującej parametry, zaczynającej się od raw **0x1CE8**, firmware ładuje:

- raw 0x2C3C → **0x200208EC** do r4
- r5 zostaje później ustawione jako **r4 + 0x08 = 0x200208F4**
- raw 0x2C44 → 0x20024630 do r7, ale przy rejestracji obwodu CO1 firmware wykonuje **0x809A: `movs r7,#0`**

Następnie są trzy konkretne rejestracje:

### 0x2032

Raw **0x8254..0x825E**:
- `r1 = r7 + 0x2000 + 0x32`
- po `r7=0`: **r1 = 0x2032**
- `r2 = r5 + 0x70`
- ponieważ r5 = 0x200208F4: **r2 = 0x20020964**
- BL 0x1143C.

To jest dokładnie adres RAM przypisany w CSV do parametru **0x2032**.

### 0x2048

Raw **0x82CE..0x82D8**:
- **r1 = 0x2048**
- `r2 = r5 + 0x72 = 0x20020966`
- BL 0x1143C.

To również zgadza się dokładnie z mapą RAM parametru **0x2048**.

### 0x2064

Raw **0x83BA..0x83C4**:
- **r1 = 0x2064**
- `r2 = r5 + 0x7A = 0x2002096E`
- BL 0x1143C.

To jest ważna korekta względem wcześniejszego uproszczenia: **0x2064 nie wskazuje na 0x20020968; firmware wskazuje na 0x2002096E**, zgodnie z tabelą parametrów.

## Kolejne potwierdzone rejestracje

Z tej samej funkcji:

| CAN index | r2 / źródło | wyliczony adres |
|---|---:|---:|
| 0x2032 | r5+0x70 | **0x20020964** |
| 0x2048 | r5+0x72 | **0x20020966** |
| 0x2166 | r5+0x74 | **0x20020968** |
| 0x2064 | r5+0x7A | **0x2002096E** |
| 0x22A5 | r5+0x81 | **0x20020975** |
| 0x22AD | r5+0x78 | **0x2002096C** |
| 0x22B1 | r5+0x93 | **0x20020987** |
| 0x2142 | r5+0x82 | **0x20020976** |
| 0x2146 | r5+0x83 | **0x20020977** |
| 0x214A | r5+0x62 | **0x20020956** |
| 0x22B5 | r5+0x6A | **0x2002095E** |
| 0x22B9 | r5+0x6E | **0x20020962** |
| 0x22BD | r5+0x76 | **0x2002096A** |
| 0x22C1 | r5+0x7C | **0x20020970** |
| 0x22C5 | r5+0x86 | **0x2002097A** |
| 0x400C | r5+0x87 | **0x2002097B** |
| 0x22C9 | r5+0x88 | **0x2002097C** |
| 0x22CD | r5+0x89 | **0x2002097D** |
| 0x22D1 | r5+0x92 | **0x20020986** |
| 0x22D5 | r5+0x8A | **0x2002097E** |
| 0x22D9 | r5+0x8B | **0x2002097F** |
| 0x22E5 | r5+0x8E | **0x20020982** |
| 0x22E9 | r5+0x8F | **0x20020983** |
| 0x22F1 | r5+0x91 | **0x20020985** |
| 0x22F9 | r5+0x9C | **0x20020990** |
| 0x2315 | r5+0x9D | **0x20020991** |
| 0x2321 | r5+0xA0 | **0x20020994** |
| 0x2325 | r5+0xA4 | **0x20020998** |
| 0x2329 | r5+0xA8 | **0x2002099C** |

Adresy wynikają bezpośrednio z instrukcji ARM i wartości r4/r5 załadowanych przez firmware.

## Rodziny indeksów — co już widać w kodzie

W tym samym bloku firmware rejestruje bazowe indeksy rodzin:

- 0x2032
- 0x2048
- 0x2064
- 0x2126, 0x212A, ... 0x213E
- 0x2142, 0x2146, 0x214A
- 0x2166
- 0x2299, 0x229D, 0x22A1, 0x22A5, 0x22AD, 0x22B1, 0x22B5, 0x22B9, 0x22BD, 0x22C1, 0x22C5, 0x22C9, 0x22CD, 0x22D1, 0x22D5, 0x22D9, 0x22E5, 0x22E9, 0x22F1, 0x22F5, 0x22F9, 0x22FD, ...
- 0x4001 i 0x400C występują w tym mechanizmie jako indeksy bazowe.

## Bardzo ważne ograniczenie

Na tym etapie mamy **bezpośredni dowód CAN index -> RAM dla pierwszej instancji (CO1)**.

Nie znaleźliśmy jeszcze w tej konkretnej funkcji osobnych BL 0x1143C dla:
- 0x2033
- 0x2034
- 0x2035
- 0x2049..0x204B
- 0x2065..0x2067
- itd.

To nie oznacza, że CO2 nie jest rejestrowane. Oznacza tylko, że jego rejestracja musi być wykonana innym mechanizmem niż proste kolejne wywołania widoczne w tym bloku.

Jednocześnie 0x1167A nadal twardo pokazuje mechanizm wyszukiwania czterech kolejnych rekordów oddalonych o 0x2C.

## Co dalej

Najważniejszy następny krok to znaleźć **jak firmware tworzy rekordy 2–4 dla parametrów count=4** oraz skąd bierze ich r2.

Mamy już bardzo dobry punkt zaczepienia:
- baza danych parametrów: **0x200208EC**
- CO1 source objects: konkretne adresy **0x200209xx**
- rejestracja: **0x1143C**
- lookup instancji: **0x1167A**
- konwersja źródła typu: **0x14728**

Następny cel to złapać pierwszy przypadek, w którym indeks **0x2033 / 0x2049 / 0x2065 / 0x4002** trafia do rekordu. Wtedy będziemy mogli zamknąć dokładny model CO2 bez zgadywania.

## Status

- [FW] pojedynczy rekord rejestracji = 0x2C bajtów.
- [FW] +0x08 = indeks.
- [FW] +0x0C = r2, wskaźnik źródła danych.
- [FW] 0x1167A wybiera jedną z czterech kolejnych instancji co 0x2C.
- [FW] funkcja rejestrująca parametry używa bazy **0x200208EC**.
- [FW] dla CO1: r5 = **0x200208F4**.
- [FW] **0x2032 -> 0x20020964**.
- [FW] **0x2048 -> 0x20020966**.
- [FW] **0x2064 -> 0x2002096E**.
- [FW] kolejne CO1 indeksy mają bezpośrednio wyliczalne adresy RAM.
- [NIEUDOWODNIONE] dokładny r2/RAM dla CO2 i CO3/CO4.
- [NIEUDOWODNIONE] czy wszystkie cztery rekordy są tworzone przez ten sam blok rejestracji.
