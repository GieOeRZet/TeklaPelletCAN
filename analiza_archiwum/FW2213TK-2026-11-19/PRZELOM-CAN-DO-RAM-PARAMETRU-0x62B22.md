# FW2213TK — przełom: pełna ścieżka CAN → rekord parametru → RAM panelu

## Najważniejsze odkrycie

Znalazłem rzeczywistą ścieżkę odbioru danych CAN, która kończy się w `0x11812`.

### 1. Odbiór ramki

Funkcja raw `0x62AE4` otrzymuje obiekt `r4` i wskaźnik `r5` do odebranej ramki.

Sprawdza:
- `[r5]` w zakresie `0x240..0x257` dla jednej gałęzi
- dla `0x584` wykonuje dalszą obsługę
- z `[r5+3]` wybiera odpowiedni typ/komendę
- dla właściwego przypadku wywołuje `0x62B22(r4, r5)`.

### 2. `0x62B22` dekoduje indeks CAN

Na początku:
- `r5 = frame`
- `r6 = [r5+4] | ([r5+5] << 8)`
- więc `r6` jest 16-bitowym indeksem parametru.

Dalej `r6` jest przekazywane do funkcji parametrów.

Przykładowo firmware rozróżnia typ danych na podstawie wartości zwróconej przez `0x115F6`, która odczytuje z rekordu bieżący typ parametru.

### 3. `0x115F6` pobiera aktualny parametr

`0x115F6(table, index, ...)` wyszukuje rekord po indeksie.
Po znalezieniu:
- `record+0x0C` jest traktowane jako wskaźnik do lokalnego storage;
- `*[record+0x0C]` jest odczytywane jako bieżąca wartość;
- `record+0x10` jest zwracane jako typ.

To potwierdza, że `record+0x0C` jest lokalnym miejscem bieżącej wartości, a nie tylko metadanymi.

### 4. Dekodowanie danych z ramki

`0x62B22` wybiera sposób dekodowania na podstawie typu:
- typ 1: 1 bajt z ramki `[r5+7]`
- typ 2: 16 bitów z `[r5+7..8]`
- typ 3: 32 bity z `[r5+7..10]`
- typ 4: signed 16-bit z `[r5+7..8]`
- typ 5: 32-bit z `[r5+7..10]`.

Po zbudowaniu lokalnego 5-bajtowego deskryptora wywołuje:
`0x11812(record_table, r6, value)`.

### 5. `0x11812` zapisuje wartość do lokalnego RAM

`0x11812` wyszukuje rekord po `r6` i następnie:
- `r7 = record + 0x0C`
- `type = record+0x10`
- dla typu 1 zapisuje bajt pod `*[r7]`
- dla typu 2 zapisuje halfword pod `*[r7]`
- dla typów 3/5 zapisuje word pod `*[r7]`
- dla typu 4 zapisuje signed halfword pod `*[r7]`.

To jest bezpośredni dowód [FW], że odebrana wartość parametru z CAN trafia przez rekord do lokalnego storage wskazanego przez `record+0x0C`.

## 6. CO1/CO2 w tej ścieżce

Dla rodziny temperatur komfortowych rejestracja tworzy:
- `0x2032 -> record -> +0x0C = 0x20020964`
- `0x2033 -> record -> +0x0C = 0x20020964`
- `0x2034 -> record -> +0x0C = 0x20020964`
- `0x2035 -> record -> +0x0C = 0x20020964`.

Zatem gdy przyjdzie CAN index `0x2033`, `0x62B22` przekazuje `0x2033` do `0x11812`, a `0x11812` wybiera rekord CO2. Ten rekord wskazuje ten sam lokalny storage `0x20020964`.

Analogicznie dla `0x2048..0x204B` i `0x2064..0x2067`.

## 7. Co to oznacza dla architektury panelu

Teraz mamy już potwierdzony przepływ:

`CAN frame`
→ `0x62AE4`
→ `0x62B22`
→ indeks 16-bitowy z `[frame+4..5]`
→ wyszukanie rekordu
→ `record+0x0C`
→ zapis wartości według `record+0x10`
→ lokalny RAM panelu
→ UI może odczytać wartość z tego RAM-u.

To jest pierwszy pełny, potwierdzony kodowo most pomiędzy magistralą CAN a parametrem używanym przez panel.

## Ważna korekta

Nie należy już mówić, że `0x2033` jest tylko logicznym aliasem `0x2032`.
`0x2033` jest osobnym rekordem w tabeli parametrów i osobnym indeksem CAN. Dopiero `record+0x0C` wskazuje wspólne lokalne storage.

## Następny cel

Pozostaje ustalić, jak UI wybiera aktywną instancję i jak odczytuje lokalny storage dla konkretnego parametru. Mamy już osobno funkcje `0x370C0/0x37094` do odczytu wartości oraz `0x37212` do zapisu według `base + instance - 1`.

To daje możliwość połączenia CAN → RAM → API parametru → UI.