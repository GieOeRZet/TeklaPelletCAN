# CO2 — analiza instancji parametrów po korelacji z firmware (2026-11-18)

## Cel
Ustalić, czy parametry z `count=4` są rzeczywiście instancjami czterech obiegów oraz jak wskazywana jest instancja CO2.

## Twardy dowód z rejestracji parametrów

W kodzie rejestrującym parametry znajduje się wspólny blok dla parametrów CO.

Dla:
- `0x2032` CH comf temp set
- `0x2048` CH eco temp set
- `0x2064` CH program

kod ustawia wskaźniki danych odpowiednio jako:
- `r5 + 0x70`
- `r5 + 0x72`
- `r5 + 0x7A`

Z katalogu RAM wynika:
- `0x2032 -> 0x20020964`
- `0x2048 -> 0x20020966`
- `0x2064 -> 0x2002096E`

Zatem podczas tej rejestracji:
- `r5 = 0x200208F4` dla pierwszego pola `CH needed temp` **jeżeli traktujemy adres pola jako bezpośredni wskaźnik**; dokładniejsza obserwacja kodu pokazuje, że lokalna baza `r5` jest przesunięta względem szerszego bloku i nie należy jej jeszcze utożsamiać z początkiem całej struktury.

### Jeszcze mocniejsza korelacja
W kodzie:
- `CH needed temp (0x22F5)` ma RAM `0x200208F4`
- rejestracja komfortowej temperatury używa `r5+0x70` i daje `0x20020964`
- eco używa `r5+0x72` i daje `0x20020966`
- res używa `r5+0x7C` i daje `0x20020970` itd.

To pokazuje, że parametry CO są polami jednego zwartego bloku danych, a nie przypadkowym zestawem niezależnych zmiennych.

## Ważna obserwacja o count=4

Parametry mają `count=4`, ale pojedynczy wpis rejestracyjny nie zawiera prostego pola „count” w podstawowym deskryptorze.

Deskryptor parametru ma m.in.:
- ID,
- wskaźnik danych,
- typ,
- zakresy/wartości metadanych.

Genericzny zapis parametru wybiera deskryptor po ID i zapisuje przez wskaźnik danych.

**Nie znaleźliśmy jeszcze w tym kroku kodu, który jednoznacznie pokazuje wzór:**
`address_CO2 = address_CO1 + stride`.

Dlatego NIE wpisujemy jeszcze arbitralnie np. `+0xB8` jako stride.

## Co jest już udowodnione

1. `0x2032`, `0x2048`, `0x2064` są elementami tego samego modelu danych CO.
2. Firmware rejestruje je z jednym bazowym blokiem danych i różnymi offsetami pól.
3. Katalog parametrów oznacza te indeksy jako `count=4`.
4. `0x4001` (CH temp measured) również ma `count=4`.
5. `0x400C` (CH temp for -10C) również ma `count=4`.
6. `0x2065 -> panel ID 168 = Tryb CO 2` jest niezależnym, bezpośrednio potwierdzonym parametrem drugiego obiegu.
7. Instrukcja Estyma potwierdza, że CO2 jest drugim fizycznym obiegiem z własną pompą, mieszaczem, czujnikiem CO2 i czujnikiem pokojowym.

## Najważniejsza rzecz do dalszego reverse engineeringu

Teraz trzeba znaleźć funkcję, która dla parametru wieloinstancyjnego wybiera instancję 0/1/2/3.

Szukamy wzorca:
- parametr ID,
- numer instancji,
- mnożenie przez stały stride,
- adres pola w bloku CO.

Dopiero znalezienie tego wzorca pozwoli zapisać bez znaku zapytania:
- CO1 = instancja 0
- CO2 = instancja 1
- CO3 = instancja 2
- CO4 = instancja 3

oraz wyliczyć dokładne RAM-y CO2 dla każdego parametru.

## Status
**[FW — potwierdzone]** model parametrów CO i ich wspólny blok danych.

**[FW — potwierdzone]** wieloinstancyjność `count=4`.

**[FW — niepotwierdzone]** dokładny stride między instancjami.

**[FW — potwierdzone]** `0x2065` = Tryb CO2.

**[Dokumentacja Estyma]** CO2 = drugi fizyczny obieg grzewczy.

Następny etap: wyszukanie kodu indeksowania instancji i jego bezpośrednie połączenie z parametrami `0x2032/0x2048/0x4001/0x400C`.
