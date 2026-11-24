# 2026-11-19 — CO instances: brak klonowania rekordów w rejestratorze, właściwy mechanizm modułu

## Nowy twardy wynik

Dalsze śledzenie potwierdziło, że funkcja rejestrująca parametry `0x0802143C` **nie tworzy automatycznie czterech rekordów** dla parametrów `count=4`.

Dla każdego wywołania tworzy dokładnie jeden rekord `0x2C`:

- `record+0x08` = indeks CAN,
- `record+0x0C` = źródło wartości przekazane przez caller.

Nie ma w tej funkcji pętli/rozszerzenia jednego indeksu na `+1,+2,+3`.

## Funkcja `0x0802143C`

Wprost:

`record = table_base + slot * 0x2C`

następnie:

`[record+0x08] = r1`

`[record+0x0C] = r2`

oraz trzy struktury pomocnicze przez `0x14728`.

Czyli dodatkowe rekordy CO2/CO3/CO4 muszą być dostarczone inną ścieżką albo przez osobne rejestracje.

## Nowa obserwacja: `0x08037D00`

To jest część obsługi/konfiguracji modułu.

`0x37D00`:

1. wywołuje `0x37DEC`,
2. wynik klasyfikuje stan/moduł,
3. dla odpowiedniej gałęzi ustawia:

`[module + 0x12C] = 1/2/3/4`

Dokładny fragment:

- case -> `r0=1`
- case -> `r0=2`
- case -> `r0=3`
- case -> `r0=4`
- następnie `strb [module+0x12C]`.

To jest kolejny bezpośredni dowód, że `+0x12C` jest rzeczywistym numerem instancji modułu.

## `0x08037DEC`

Ta funkcja czyta:

`module + 0x128 + 2`

i na tej podstawie klasyfikuje moduł.

Dla jednej z klas zwraca 1/2 itd., a dla pozostałych ścieżek 0/6.

Nie przypisujemy jeszcze nazw tych klas do CO1/CO2 — tego firmware w tym miejscu nie mówi wprost.

## `0x08037212`

To ważne, bo pokazuje drugi użytek numeru instancji.

Funkcja:

- pobiera aktualny `module+0x12C`,
- przeszukuje tabelę bazowych parametrów,
- wykonuje:

`base_index + instance - 1`

- i przekazuje wynik do `0x11812`.

Czyli dla parametru bazowego `0x2032` i instancji 2 powstaje `0x2033`.

To jest ścieżka **zapisu/aktualizacji parametru**, nie tworzenia rekordu.

## Kluczowa korekta modelu

Mamy teraz rozdzielone trzy mechanizmy:

### A. Rejestracja

`0x1143C`

Tworzy rekord:

`CAN index -> source pointer/value`

jeden rekord na wywołanie.

### B. Lookup

`0x1167A`

Szuka dokładnego indeksu w tabeli `0x20008D84`, sprawdzając 4 rekordy po `0x2C`.

### C. Dostęp modułowy

`0x370C0 / 0x37212`

robi:

`base + instance - 1`

i dopiero z tym indeksem wykonuje lookup/read/write.

## Co z tego wynika

Nie będziemy już szukać „funkcji, która kopiuje 0x2C rekord 4 razy” jako założenia.

Firmware może robić to w jednej z dwóch rzeczywistych form:

1. **osobna rejestracja dynamiczna** z indeksem wynikającym z instancji,
2. albo rekordy instancji są tworzone przez inną warstwę inicjalizacji modułu.

Statyczna funkcja `0x1143C` sama tego nie robi.

## Następny cel

Teraz trzeba prześledzić **moment inicjalizacji konkretnego modułu CO expansion**:

`module object`
-> `+0x128`
-> `+0x12C = instance`
-> utworzenie jego parametrów
-> ewentualne wywołania `0x1143C`

To jest najkrótsza droga do odpowiedzi:

**CO2 index -> dokładny CO2 RAM/source pointer**

bez zgadywania stałego przesunięcia RAM.
